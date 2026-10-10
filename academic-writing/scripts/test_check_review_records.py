#!/usr/bin/env python3
"""CLI regressions for review evidence structure, never for prose quality.

Run with ``python3 -m unittest discover -s scripts -p 'test_*.py' -v`` from
the skill directory. Fixtures use temporary files and only standard libraries.
The fixtures do not call the validator's own validation or inventory helpers.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("check_review_records.py")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class ReviewRecordCLIRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="review-record-regression-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog_path = self.root / "catalog.json"
        self.record_path = self.root / "record.json"
        self.record_snapshot = self.root / "record.snapshot.json"
        self.rule_path = self.root / "rules.md"
        self.rule_blocks = [
            "每段必须交代对象；每段必须交代条件。",
            "所有判断必须保留原文短引。",
        ]
        self.rule_path.write_text(
            "# 规则\n\n" + "\n\n".join(self.rule_blocks) + "\n", encoding="utf-8"
        )
        self.old_quotes = [
            "P1 在固定样本中，模型以误差衡量结果。",
            "P2 数据增加时，波动减少。",
        ]
        self.current_quotes = [
            "P1 在固定样本中，模型以平均误差衡量结果。",
            "P2 在相同训练条件下，数据增加时，波动减少。",
        ]
        self.notes_quote = "建议补充平均误差和训练条件；这段建议尚未写回正文。"
        self.artifacts = {}
        for key, path, quotes, version, kind in (
            ("old", "source-old.md", self.old_quotes, "V1", "source"),
            ("current", "source-current.md", self.current_quotes, "V2", "source"),
            ("notes", "notes.md", [self.notes_quote], "N1", "review_notes"),
        ):
            raw = ("# 材料\n\n" + "\n\n".join(quotes) + "\n").encode("utf-8")
            (self.root / path).write_bytes(raw)
            snapshot = "snapshot-" + path
            (self.root / snapshot).write_bytes(raw)
            self.artifacts[key] = {
                "path": path, "sha256": sha(raw), "version": version, "kind": kind,
                "recoverable": {"kind": "snapshot", "path": snapshot},
            }
        self.catalog = {
            "sources": [{"path": "rules.md", "sha256": sha(self.rule_path.read_bytes())}],
            "coverage": [], "criteria": [],
        }
        statements = [
            ["每段必须交代对象；", "每段必须交代条件。"],
            ["所有判断必须保留原文短引。"],
        ]
        for index, block in enumerate(self.rule_blocks):
            criterion_id = "R" + str(index + 1)
            line = 3 + index * 2
            requirements = [
                {
                    "id": criterion_id + "." + sha(("rules.md" + r"\n" + atom).encode())[:10],
                    "statement": atom, "file": "rules.md", "start": line, "end": line,
                }
                for atom in statements[index]
            ]
            self.catalog["criteria"].append({
                "id": criterion_id, "title": "最小规则 " + criterion_id,
                "applies": "声明范围内的段落与审查判断",
                "action": "读取 P1 与 P2，分别核对规则的每个子要求",
                "evidence": "正文短引、段落标识与判断依据",
                "fail": "缺对象、条件或定位证据时登记问题",
                "sources": [{"file": "rules.md", "quote": block}],
                "requirements": requirements,
            })
            self.catalog["coverage"].append({
                "file": "rules.md", "start": line, "end": line, "sha256": sha(block.encode()),
                "kind": "requirement", "criteria": [criterion_id],
                "clauses": [{"sha256": sha(atom.encode()), "criteria": [criterion_id]}
                            for atom in statements[index]],
            })
        self.catalog_path.write_bytes(json_bytes(self.catalog))
        current = self.artifacts["current"]
        self.record = {
            "schema_version": 1, "record_id": "REGRESSION-1", "revision": "R1",
            "date": "2026-10-10", "catalog_sha256": sha(self.catalog_path.read_bytes()),
            "reviewer": {"name": "审查代理 A", "role": "AI 自查"},
            "recoverable": {"kind": "snapshot", "path": self.record_snapshot.name},
            "scope": {
                "target": "source-current.md 的 P1 与 P2",
                "targets": [{"artifact": "current", "path": current["path"],
                             "sha256": current["sha256"], "version": current["version"],
                             "range": "P1 与 P2"}],
                "required_criteria": ["R1", "R2"],
            },
            "artifacts": copy.deepcopy(self.artifacts), "findings": {}, "checks": [],
            "conclusions": {"record": "accepted", "text": "passed"},
            "audit": {"reviewer": "复核代理 B，AI 记录复核", "scope": "两段正文及完整记录",
                      "evidence": self.evidence()},
        }
        for criterion in self.catalog["criteria"]:
            check = {
                "criterion_id": criterion["id"], "status": "pass",
                "units": ["P1", "P2"], "applicable_units": ["P1", "P2"],
                "performed_action": "读取 P1 和 P2，分别核对对象、条件与短引",
                "reason": "两个声明单元均保留可定位的对象、条件及原文",
                "evidence": self.evidence(), "findings": [], "subchecks": [],
            }
            for requirement in criterion["requirements"]:
                check["subchecks"].append({
                    "requirement_id": requirement["id"], "status": "pass",
                    "units": ["P1", "P2"], "applicable_units": ["P1", "P2"],
                    "performed_action": "逐段核对：" + requirement["statement"],
                    "reason": "P1、P2 均提供此子要求对应的正文依据",
                    "evidence": self.evidence(),
                })
            self.record["checks"].append(check)
        self.persist_record(self.record)

    def evidence(self, artifact="current"):
        quotes = {"current": self.current_quotes, "old": self.old_quotes,
                  "notes": [self.notes_quote]}[artifact]
        return [{"artifact": artifact, "quote": quote, "locator": "P" + str(index + 1),
                 "explanation": "短引保留了本次判断使用的对象及上下文条件"}
                for index, quote in enumerate(quotes)]

    def invoke(self, *arguments):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                              capture_output=True, text=True, timeout=15)

    def persist_record(self, record, recover=True):
        raw = json_bytes(record)
        self.record_path.write_bytes(raw)
        if recover:
            self.record_snapshot.write_bytes(raw)

    def run_record(self, record=None, recover=True):
        self.persist_record(self.record if record is None else record, recover=recover)
        return self.invoke("record", "--root", self.root, "--catalog", self.catalog_path,
                           "--record", self.record_path)

    def run_catalog(self, catalog=None):
        if catalog is not None:
            self.catalog_path.write_bytes(json_bytes(catalog))
        return self.invoke("catalog", "--root", self.root, "--catalog", self.catalog_path)

    def assert_rejected(self, result, diagnostic=None):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if diagnostic:
            self.assertIn(diagnostic, result.stderr)

    def attach_closed_finding(self, record):
        record["findings"]["F1"] = {
            "status": "closed", "before_source": "old", "after_source": "current",
            "before": self.evidence("old"), "after": self.evidence("current"),
            "reread": {"reviewer": "复读代理 B", "version": "V2", "scope": "P1 与 P2",
                       "evidence": self.evidence("current")},
        }
        record["checks"][0]["findings"] = ["F1"]

    def attach_withdrawn_finding(self, record):
        record["findings"]["F1"] = {
            "status": "withdrawn", "original_source": "current",
            "before": self.evidence("current"), "counterevidence": self.evidence("current"),
            "reread": {"reviewer": "复读代理 B", "version": "V2", "scope": "P1 与 P2",
                       "evidence": self.evidence("current")},
        }
        record["checks"][0]["findings"] = ["F1"]

    def test_valid_catalog_and_record_pass_cli(self):
        for result in (self.run_catalog(), self.run_record()):
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("不代表阅读判断正确或正文通过", result.stdout)

    def test_valid_closed_finding_passes(self):
        record = copy.deepcopy(self.record)
        self.attach_closed_finding(record)
        result = self.run_record(record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_valid_withdrawal_passes_without_manufactured_revision(self):
        record = copy.deepcopy(self.record)
        self.attach_withdrawn_finding(record)
        result = self.run_record(record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_acceptance_does_not_require_text_acceptance(self):
        record = copy.deepcopy(self.record)
        record["findings"]["F1"] = {"status": "open", "before": self.evidence()}
        record["checks"][0].update(status="fail", findings=["F1"])
        record["conclusions"]["text"] = "needs_revision"
        result = self.run_record(record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_rule_check_rejected(self):
        record = copy.deepcopy(self.record)
        record["checks"].pop()
        self.assert_rejected(self.run_record(record), "规则检查遗漏")

    def test_unregistered_rule_sources_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["sources"] = []
        catalog["coverage"] = []
        self.assert_rejected(self.run_catalog(catalog), "来源文件未登记")

    def test_missing_rule_block_coverage_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["coverage"].pop()
        self.assert_rejected(self.run_catalog(catalog), "规则块覆盖有遗漏")

    def test_duplicate_rule_sources_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["sources"].append(copy.deepcopy(catalog["sources"][0]))
        self.assert_rejected(self.run_catalog(catalog), "规则来源清单为空或重复")

    def test_missing_composite_catalog_requirement_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["criteria"][0]["requirements"].pop()
        self.assert_rejected(self.run_catalog(catalog), "子要求映射缺失")

    def test_missing_rule_clause_coverage_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["coverage"][0]["clauses"].pop()
        self.assert_rejected(self.run_catalog(catalog), "规则原句覆盖遗漏")

    def test_unknown_rule_clause_owner_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["coverage"][0]["clauses"][0]["criteria"] = ["UNKNOWN"]
        self.assert_rejected(self.run_catalog(catalog), "规则原句缺审查项映射")

    def test_rule_block_and_clause_owners_must_agree(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["coverage"][0]["criteria"].append("R2")
        self.assert_rejected(self.run_catalog(catalog), "规则块与逐句归属不一致")

    def split_first_block_between_rules(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["coverage"][0]["criteria"] = ["R1", "R2"]
        catalog["coverage"][0]["clauses"][1]["criteria"] = ["R2"]
        transferred = catalog["criteria"][0]["requirements"].pop()
        transferred["id"] = "R2." + sha(("rules.md" + r"\n" + transferred["statement"]).encode())[:10]
        catalog["criteria"][1]["requirements"].insert(0, transferred)
        return catalog

    def test_valid_clause_owners_do_not_copy_whole_block_to_each_rule(self):
        catalog = self.split_first_block_between_rules()
        result = self.run_catalog(catalog)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_copying_other_rule_clause_as_own_requirement_rejected(self):
        catalog = self.split_first_block_between_rules()
        catalog["criteria"][0]["requirements"] = copy.deepcopy(self.catalog["criteria"][0]["requirements"])
        self.assert_rejected(self.run_catalog(catalog), "子要求映射缺失或与原文不符")

    def test_inline_bold_title_stays_with_following_instruction(self):
        catalog = copy.deepcopy(self.catalog)
        label = "**段落要件。** "
        first_block = label + self.rule_blocks[0]
        self.rule_path.write_text("# 规则\n\n" + first_block + "\n\n" + self.rule_blocks[1] + "\n",
                                  encoding="utf-8")
        catalog["sources"][0]["sha256"] = sha(self.rule_path.read_bytes())
        catalog["coverage"][0]["sha256"] = sha(first_block.encode())
        catalog["criteria"][0]["sources"][0]["quote"] = first_block
        first_requirement = catalog["criteria"][0]["requirements"][0]
        first_requirement["statement"] = label + first_requirement["statement"]
        first_requirement["id"] = "R1." + sha(("rules.md" + r"\n" + first_requirement["statement"]).encode())[:10]
        catalog["coverage"][0]["clauses"][0]["sha256"] = sha(first_requirement["statement"].encode())
        self.assertEqual(len(catalog["criteria"][0]["requirements"]), 2)
        result = self.run_catalog(catalog)
        self.assertEqual(result.returncode, 0, result.stderr)

    def catalog_with_first_rule_atoms(self, atoms):
        catalog = copy.deepcopy(self.catalog)
        first_block = "".join(atoms)
        self.rule_path.write_text("# 规则\n\n" + first_block + "\n\n" + self.rule_blocks[1] + "\n",
                                  encoding="utf-8")
        catalog["sources"][0]["sha256"] = sha(self.rule_path.read_bytes())
        catalog["coverage"][0]["sha256"] = sha(first_block.encode())
        catalog["coverage"][0]["clauses"] = [
            {"sha256": sha(atom.encode()), "criteria": ["R1"]} for atom in atoms
        ]
        catalog["criteria"][0]["sources"][0]["quote"] = first_block
        catalog["criteria"][0]["requirements"] = [
            {"id": "R1." + sha(("rules.md" + r"\n" + atom).encode())[:10],
             "statement": atom, "file": "rules.md", "start": 3, "end": 3}
            for atom in atoms
        ]
        return catalog

    def test_double_quoted_template_punctuation_stays_in_one_requirement(self):
        atoms = ["检查模板“对象已明确。条件仍待核实；尚不应验收。”是否给出判断依据。"]
        result = self.run_catalog(self.catalog_with_first_rule_atoms(atoms))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_single_quoted_template_punctuation_stays_in_one_requirement(self):
        atoms = ["检查模板‘对象已明确。条件仍待核实；尚不应验收。’是否给出判断依据。"]
        result = self.run_catalog(self.catalog_with_first_rule_atoms(atoms))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_nested_chinese_quoted_templates_stay_in_one_requirement(self):
        for statement in (
            "检查“作者写道‘对象明确。条件待核实；不可验收。’但未给依据。”所指的条件。",
            "检查‘作者写道“对象明确。条件待核实；不可验收。”但未给依据。’所指的条件。",
        ):
            with self.subTest(statement=statement):
                result = self.run_catalog(self.catalog_with_first_rule_atoms([statement]))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_unquoted_punctuation_still_separates_requirements(self):
        atoms = ["检查“对象明确。条件待核实；尚不可验收。”的适用范围；",
                 "为引号之外的结论提供正文证据。"]
        result = self.run_catalog(self.catalog_with_first_rule_atoms(atoms))
        self.assertEqual(result.returncode, 0, result.stderr)

    def catalog_with_nonrequirement_clause(self, kind="illustration"):
        catalog = copy.deepcopy(self.catalog)
        texts = {"illustration": "例如，P1 可说明一个条件。",
                 "navigation": "具体核对步骤见下一节。",
                 "reference": "参考材料为项目提供的写作指南。"}
        statement = texts.get(kind, texts["illustration"])
        first_block = self.rule_blocks[0] + statement
        self.rule_path.write_text("# 规则\n\n" + first_block + "\n\n" + self.rule_blocks[1] + "\n",
                                  encoding="utf-8")
        catalog["sources"][0]["sha256"] = sha(self.rule_path.read_bytes())
        catalog["coverage"][0]["sha256"] = sha(first_block.encode())
        catalog["coverage"][0]["clauses"].append({
            "sha256": sha(statement.encode()), "kind": kind, "criteria": [],
            "reason": "此句只提供示例、导航或参考位置，没有新增写作约束",
        })
        return catalog

    def test_documented_nonrequirement_clause_exclusions_pass(self):
        for kind in ("illustration", "navigation", "reference"):
            with self.subTest(kind=kind):
                result = self.run_catalog(self.catalog_with_nonrequirement_clause(kind))
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_nonrequirement_clause_without_reason_rejected(self):
        catalog = self.catalog_with_nonrequirement_clause()
        del catalog["coverage"][0]["clauses"][-1]["reason"]
        self.assert_rejected(self.run_catalog(catalog), "非约束原句排除无依据")

    def test_nonrequirement_clause_with_blank_reason_rejected(self):
        catalog = self.catalog_with_nonrequirement_clause()
        catalog["coverage"][0]["clauses"][-1]["reason"] = " "
        self.assert_rejected(self.run_catalog(catalog), "非约束原句排除无依据")

    def test_nonrequirement_clause_with_invalid_kind_rejected(self):
        catalog = self.catalog_with_nonrequirement_clause()
        catalog["coverage"][0]["clauses"][-1]["kind"] = "ignore-anything"
        self.assert_rejected(self.run_catalog(catalog), "非约束原句排除无依据")

    def test_nonrequirement_clause_cannot_claim_rule_owner(self):
        catalog = self.catalog_with_nonrequirement_clause()
        catalog["coverage"][0]["clauses"][-1]["criteria"] = ["R1"]
        self.assert_rejected(self.run_catalog(catalog), "非约束原句排除无依据")

    def test_clause_defaults_to_requirement_and_needs_owner(self):
        catalog = self.catalog_with_nonrequirement_clause()
        del catalog["coverage"][0]["clauses"][-1]["kind"]
        self.assert_rejected(self.run_catalog(catalog), "规则原句缺审查项映射")

    def test_rule_file_drift_rejected_by_record_cli(self):
        with self.rule_path.open("a", encoding="utf-8") as stream:
            stream.write("\n新增规则：必须区分已读和未读对象。\n")
        self.assert_rejected(self.run_record(), "规则已变化")

    def test_record_catalog_version_mismatch_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["criteria"][0]["title"] = "规则标题的新版本"
        self.catalog_path.write_bytes(json_bytes(catalog))
        self.assert_rejected(self.run_record(), "记录绑定的规则版本不匹配")

    def test_body_version_drift_rejected(self):
        with (self.root / "source-current.md").open("a", encoding="utf-8") as stream:
            stream.write("\n新增但尚未审查的段落。\n")
        self.assert_rejected(self.run_record(), "证据版本已变化")

    def test_empty_and_whitespace_evidence_fields_rejected(self):
        for field, value, diagnostic in (
            ("quote", "\n", "短引为空白"),
            ("locator", " ", "缺定位"),
            ("explanation", " ", "缺判断依据"),
        ):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record["checks"][0]["evidence"][0][field] = value
                self.assert_rejected(self.run_record(record), diagnostic)

    def test_empty_evidence_collection_rejected(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["evidence"] = []
        self.assert_rejected(self.run_record(record), "R1缺少证据")

    def test_blank_identity_and_target_rejected(self):
        for path in (("reviewer", "name"), ("reviewer", "role"), ("scope", "target")):
            with self.subTest(path=path):
                record = copy.deepcopy(self.record)
                record[path[0]][path[1]] = " "
                self.assert_rejected(self.run_record(record), "记录身份或范围为空白")

    def test_blank_actual_action_rejected(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["performed_action"] = " "
        self.assert_rejected(self.run_record(record), "缺实际执行动作")

    def test_fake_close_using_only_notes_rejected(self):
        record = copy.deepcopy(self.record)
        self.attach_closed_finding(record)
        finding = record["findings"]["F1"]
        finding["before"] = self.evidence("notes")
        finding["after"] = self.evidence("notes")
        finding["reread"]["evidence"] = self.evidence("notes")
        self.assert_rejected(self.run_record(record), "修订证据未绑定改后正文")

    def test_close_reread_bound_to_new_version_rejected_when_wrong(self):
        record = copy.deepcopy(self.record)
        self.attach_closed_finding(record)
        record["findings"]["F1"]["reread"]["version"] = "V1"
        self.assert_rejected(self.run_record(record), "复读版本与修订正文版本不符")

    def test_close_without_different_body_versions_rejected(self):
        record = copy.deepcopy(self.record)
        self.attach_closed_finding(record)
        finding = record["findings"]["F1"]
        finding["before_source"] = "current"
        finding["before"] = self.evidence("current")
        self.assert_rejected(self.run_record(record), "没有不同正文版本")

    def test_withdrawal_using_only_notes_rejected(self):
        record = copy.deepcopy(self.record)
        self.attach_withdrawn_finding(record)
        finding = record["findings"]["F1"]
        finding["counterevidence"] = self.evidence("notes")
        finding["reread"]["evidence"] = self.evidence("notes")
        self.assert_rejected(self.run_record(record), "撤销证据未绑定原正文")

    def test_withdrawal_unknown_version_rejected(self):
        record = copy.deepcopy(self.record)
        self.attach_withdrawn_finding(record)
        record["findings"]["F1"]["reread"]["version"] = "NOT-A-REGISTERED-VERSION"
        self.assert_rejected(self.run_record(record), "撤销核验版本与原正文不符")

    def test_missing_structured_targets_rejected(self):
        record = copy.deepcopy(self.record)
        record["scope"]["targets"] = []
        self.assert_rejected(self.run_record(record), "范围未结构化绑定")

    def test_target_path_digest_and_version_mismatch_rejected(self):
        for field in ("path", "sha256", "version"):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record["scope"]["targets"][0][field] = "not-the-reviewed-target"
                self.assert_rejected(self.run_record(record), "范围目标" + field)

    def test_target_cannot_be_review_notes(self):
        record = copy.deepcopy(self.record)
        notes = record["artifacts"]["notes"]
        record["scope"]["targets"] = [{"artifact": "notes", "range": "整段建议",
                                       **{key: notes[key] for key in ("path", "sha256", "version")}}]
        self.assert_rejected(self.run_record(record), "范围目标必须绑定正文或受审记录")

    def test_old_artifacts_cannot_replace_registered_current_target(self):
        record = copy.deepcopy(self.record)
        del record["artifacts"]["current"]
        for check in record["checks"]:
            check["evidence"] = self.evidence("old")
            for subcheck in check["subchecks"]:
                subcheck["evidence"] = self.evidence("old")
        record["audit"]["evidence"] = self.evidence("old")
        self.assert_rejected(self.run_record(record), "范围目标")

    def test_old_evidence_cannot_back_current_target_pass(self):
        record = copy.deepcopy(self.record)
        for check in record["checks"]:
            check["evidence"] = self.evidence("old")
            for subcheck in check["subchecks"]:
                subcheck["evidence"] = self.evidence("old")
        record["audit"]["evidence"] = self.evidence("old")
        self.assert_rejected(self.run_record(record))

    def test_parent_pass_requires_target_bound_evidence(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["evidence"] = self.evidence("old")
        self.assert_rejected(self.run_record(record))

    def test_subcheck_pass_requires_target_bound_evidence(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["subchecks"][0]["evidence"] = self.evidence("old")
        self.assert_rejected(self.run_record(record))

    def test_valid_pass_can_include_supplementary_reference_evidence(self):
        record = copy.deepcopy(self.record)
        for check in record["checks"]:
            check["evidence"] += self.evidence("notes")
            for subcheck in check["subchecks"]:
                subcheck["evidence"] += self.evidence("notes")
        result = self.run_record(record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_recovery_missing_rejected(self):
        record = copy.deepcopy(self.record)
        record["recoverable"]["path"] = "not-stored/record.json"
        self.assert_rejected(self.run_record(record), "记录自身受审全文不能恢复")

    def test_record_recovery_stale_rejected(self):
        record = copy.deepcopy(self.record)
        record["revision"] = "R2"
        self.assert_rejected(self.run_record(record, recover=False), "记录自身受审全文不能恢复")

    def test_record_recovery_cannot_point_to_mutable_record_itself(self):
        record = copy.deepcopy(self.record)
        record["recoverable"]["path"] = self.record_path.name
        self.assert_rejected(self.run_record(record), "恢复位置不能只是正在修改的记录自身")

    def test_missing_composite_subcheck_rejected(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["subchecks"].pop()
        self.assert_rejected(self.run_record(record), "未逐项核对所有子要求")

    def test_pending_subcheck_cannot_claim_parent_pass(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["subchecks"][0].update(status="pending", missing="缺 P2 核对")
        self.assert_rejected(self.run_record(record), "子要求仍未通过")

    def test_partial_units_cannot_claim_whole_rule_pass(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["units"] = ["P1"]
        self.assert_rejected(self.run_record(record), "局部检查不能冒充全部适用单元通过")

    def test_partial_subcheck_units_cannot_claim_all_units_pass(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["subchecks"][0]["units"] = ["P1"]
        self.assert_rejected(self.run_record(record), "子要求缺完整适用单元核对")

    def test_duplicate_subcheck_units_rejected(self):
        record = copy.deepcopy(self.record)
        record["checks"][0]["subchecks"][0]["units"] = ["P1", "P2", "P2"]
        self.assert_rejected(self.run_record(record), "子要求缺完整适用单元核对")

    def test_pending_rule_cannot_claim_text_pass(self):
        record = copy.deepcopy(self.record)
        record["checks"][0].update(status="pending", missing="尚缺 P2 检查")
        self.assert_rejected(self.run_record(record), "必查项仍未通过")

    def test_partial_pending_rule_requires_action_and_evidence(self):
        for field, empty, diagnostic in (("performed_action", "", "部分检查缺实际执行动作"),
                                          ("evidence", [], "部分检查缺少证据")):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                check = record["checks"][0]
                check.update(status="pending", units=["P1"], missing="尚缺 P2 检查")
                check[field] = empty
                record["conclusions"]["text"] = "insufficient_evidence"
                self.assert_rejected(self.run_record(record), diagnostic)

    def test_partial_pending_subcheck_requires_action_and_evidence(self):
        for field, empty, diagnostic in (("performed_action", "", "子要求部分检查缺实际动作"),
                                          ("evidence", [], "子要求部分检查缺少证据")):
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record["checks"][0].update(status="pending", missing="尚缺条件核对")
                subcheck = record["checks"][0]["subchecks"][0]
                subcheck.update(status="pending", units=["P1"], missing="尚缺 P2 检查")
                subcheck[field] = empty
                record["conclusions"]["text"] = "insufficient_evidence"
                self.assert_rejected(self.run_record(record), diagnostic)

    def test_out_of_scope_requires_scope_basis(self):
        record = copy.deepcopy(self.record)
        record["checks"][0].update(status="out_of_scope", scope_basis=" ")
        record["conclusions"]["text"] = "insufficient_evidence"
        self.assert_rejected(self.run_record(record), "范围外但未说明范围依据")

    def test_subcheck_out_of_scope_requires_scope_basis(self):
        record = copy.deepcopy(self.record)
        record["checks"][0].update(status="pending", missing="部分子要求在约定范围外")
        record["checks"][0]["subchecks"][0].update(status="out_of_scope", scope_basis=" ")
        record["conclusions"]["text"] = "insufficient_evidence"
        self.assert_rejected(self.run_record(record), "子要求范围外缺约定依据")

    def test_not_applicable_requires_evidence(self):
        record = copy.deepcopy(self.record)
        record["checks"][0].update(status="not_applicable", evidence=[])
        self.assert_rejected(self.run_record(record), "R1缺少证据")

    def test_fail_requires_finding_id(self):
        record = copy.deepcopy(self.record)
        record["checks"][0].update(status="fail", findings=[])
        record["conclusions"]["text"] = "needs_revision"
        self.assert_rejected(self.run_record(record), "未通过但没有问题编号")

    def test_open_finding_blocks_text_pass_even_outside_required_rules(self):
        record = copy.deepcopy(self.record)
        record["scope"]["required_criteria"] = ["R2"]
        record["checks"][0].update(status="fail", findings=["F1"])
        record["findings"]["F1"] = {"status": "open", "before": self.evidence()}
        self.assert_rejected(self.run_record(record), "正文问题仍未关闭")

    def test_blank_reread_identity_rejected(self):
        record = copy.deepcopy(self.record)
        self.attach_closed_finding(record)
        record["findings"]["F1"]["reread"]["reviewer"] = " "
        self.assert_rejected(self.run_record(record))

    def test_blank_record_auditor_identity_rejected(self):
        record = copy.deepcopy(self.record)
        record["audit"]["reviewer"] = " "
        self.assert_rejected(self.run_record(record))

    def test_init_never_presets_pass_or_not_applicable(self):
        output = self.root / "new" / "initialized.json"
        result = self.invoke("init", "--catalog", self.catalog_path, "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(output.read_bytes())
        self.assertEqual(record["conclusions"],
                         {"record": "needs_review", "text": "insufficient_evidence"})
        self.assertEqual(record["scope"]["targets"], [])
        self.assertEqual(len(record["checks"]), len(self.catalog["criteria"]))
        for check, criterion in zip(record["checks"], self.catalog["criteria"]):
            self.assertEqual(check["status"], "pending")
            self.assertEqual(check["units"], [])
            self.assertEqual(check["performed_action"], "")
            self.assertEqual(check["evidence"], [])
            self.assertEqual(len(check["subchecks"]), len(criterion["requirements"]))
            for subcheck in check["subchecks"]:
                self.assertEqual(subcheck["status"], "pending")

    def test_init_refuses_to_overwrite_existing_record(self):
        before = self.record_path.read_bytes()
        result = self.invoke("init", "--catalog", self.catalog_path, "--output", self.record_path)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("目标已存在", result.stderr)
        self.assertEqual(self.record_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
