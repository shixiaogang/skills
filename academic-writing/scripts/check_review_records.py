#!/usr/bin/env python3
"""Validate recoverable writing-review evidence; never judge prose quality."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

STATUSES = {"pass", "fail", "pending", "not_applicable", "out_of_scope"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def recover_data(recovery, base):
    if not isinstance(recovery, dict):
        return None
    if recovery.get("kind") == "snapshot":
        path = base / recovery.get("path", "")
        return path.read_bytes() if path.is_file() else None
    if recovery.get("kind") == "git":
        try:
            return subprocess.check_output(["git", "-C", str(base / recovery["root"]), "show",
                f"{recovery['commit']}:{recovery['path']}"], stderr=subprocess.DEVNULL)
        except (KeyError, subprocess.CalledProcessError):
            return None
    return None


def blocks(text):
    """Inventory Markdown body blocks, retaining exact text and line locations."""
    lines = text.splitlines()
    result = []
    i = 0
    while i < len(lines):
        if not lines[i].strip() or lines[i].startswith("#"):
            i += 1
            continue
        start = i
        kind = "text"
        if i == 0 and lines[i] == "---":
            kind = "metadata"
            i += 1
            while i < len(lines) and lines[i] != "---":
                i += 1
            i += 1
        elif lines[i].startswith("```"):
            kind = "code"
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
            i += 1
        elif lines[i].startswith("|"):
            kind = "table"
            while i < len(lines) and lines[i].startswith("|"):
                i += 1
        elif lines[i].startswith(">"):
            kind = "quotation"
            while i < len(lines) and lines[i].startswith(">"):
                i += 1
        elif re.match(r"^(?:- |\d+\. )", lines[i]):
            i += 1
            while i < len(lines) and lines[i].startswith("   "):
                i += 1
        else:
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(?:#|```|\||>|- |\d+\. )", lines[i]):
                i += 1
        raw = "\n".join(lines[start:i])
        result.append({"start": start + 1, "end": i, "text": raw,
                       "sha256": digest(raw.encode()), "format": kind})
    return result


def need(value, message, errors):
    if isinstance(value, str):
        value = value.strip()
    if not value:
        errors.append(message)
    return bool(value)


def atoms_for(block):
    if block['format'] == 'table':
        return [s.strip() for s in block['text'].splitlines()[2:] if s.strip()]
    if block['format'] == 'code':
        return [block['text']]
    # Keep inline bold labels together with their following instruction.
    atoms, start, i, bold, code, quotes = [], 0, 0, False, False, []
    while i < len(block['text']):
        if block['text'][i:i+2] == '**' and not code:
            bold = not bold
            i += 2
            continue
        if block['text'][i] == '`':
            code = not code
        if not code:
            if block['text'][i] in '“‘':
                quotes.append('”' if block['text'][i] == '“' else '’')
            elif quotes and block['text'][i] == quotes[-1]:
                quotes.pop()
        if block['text'][i] in '。；' and not bold and not code and not quotes:
            atoms.append(block['text'][start:i+1].strip())
            start = i + 1
        i += 1
    atoms.append(block['text'][start:].strip())
    return [a for a in atoms if a]


def requirements_for(criterion_id, coverage, root):
    result, seen = [], set()
    for cover in coverage:
        if cover.get('kind') != 'requirement':
            continue
        block = next((b for b in blocks((root / cover['file']).read_text(encoding='utf-8'))
                      if b['start'] == cover['start']), None)
        if block is None:
            continue
        for atom in atoms_for(block):
            clause = next((c for c in cover.get('clauses', []) if c.get('sha256') == digest(atom.encode())), {})
            if criterion_id not in clause.get('criteria', []) or (cover['file'], atom) in seen:
                continue
            seen.add((cover['file'], atom))
            result.append({'id': criterion_id + '.' + digest((cover['file'] + '\\n' + atom).encode())[:10],
                           'statement': atom, 'file': cover['file'], 'start': cover['start'], 'end': cover['end']})
    return result


def check_catalog(catalog, root):
    errors = []
    ids = [c.get("id") for c in catalog.get("criteria", [])]
    need(ids and len(ids) == len(set(ids)), "审查项编号缺失或重复", errors)
    known = set(ids)
    sources = {s["path"]: s for s in catalog.get("sources", [])}
    need(sources and len(sources) == len(catalog.get("sources", [])), "规则来源清单为空或重复", errors)
    for criterion in catalog.get("criteria", []):
        for field in ("id", "title", "applies", "action", "evidence", "fail", "sources"):
            need(criterion.get(field), f"{criterion.get('id')}缺少{field}", errors)
        for source in criterion.get("sources", []):
            path = root / source.get("file", "")
            need(source.get("file") in sources, f"{criterion.get('id')}来源文件未登记", errors)
            need(source.get("quote"), f"{criterion.get('id')}规则短引为空白", errors)
            need(path.is_file() and source.get("quote") and source["quote"] in path.read_text(encoding="utf-8"),
                 f"{criterion.get('id')}规则原文无法定位：{source.get('file')}", errors)
    coverage = catalog.get("coverage", [])
    for relative, source in sources.items():
        path = root / relative
        if not need(path.is_file(), f"规则文件不存在：{relative}", errors):
            continue
        need(digest(path.read_bytes()) == source.get("sha256"), f"规则已变化，须重审映射：{relative}", errors)
        actual = {(b["start"], b["end"], b["sha256"]) for b in blocks(path.read_text(encoding="utf-8"))}
        registered = [(b["start"], b["end"], b["sha256"]) for b in coverage if b.get("file") == relative]
        need(len(registered) == len(set(registered)) and set(registered) == actual,
             f"规则块覆盖有遗漏、重复或失效：{relative}", errors)
    for block in coverage:
        need(block.get("file") in sources, "覆盖项指向未登记规则文件", errors)
        if block.get("kind") == "requirement":
            need(block.get("criteria") and set(block["criteria"]) <= known,
                 f"规则块缺审查项映射：{block.get('file')}:{block.get('start')}", errors)
            path = root / block.get('file', '')
            original = next((b for b in blocks(path.read_text(encoding='utf-8')) if b['start'] == block.get('start')), None) if path.is_file() else None
            if original:
                expected_clauses = [digest(a.encode()) for a in atoms_for(original)]
                actual_clauses = [c.get('sha256') for c in block.get('clauses', [])]
                need(actual_clauses == expected_clauses, f"规则原句覆盖遗漏或顺序失效：{block['file']}:{block['start']}", errors)
                mapped = set()
                for clause in block.get('clauses', []):
                    if clause.get('kind', 'requirement') == 'requirement':
                        need(clause.get('criteria') and set(clause['criteria']) <= known,
                             f"规则原句缺审查项映射：{block['file']}:{block['start']}", errors)
                    else:
                        need(clause.get('kind') in {'illustration', 'navigation', 'reference'}
                             and not clause.get('criteria') and clause.get('reason'),
                             f"非约束原句排除无依据：{block['file']}:{block['start']}", errors)
                    mapped.update(clause.get('criteria', []))
                need(mapped == set(block.get('criteria', [])), f"规则块与逐句归属不一致：{block['file']}:{block['start']}", errors)
        else:
            need(block.get("kind") in {"illustration", "navigation", "template", "metadata", "reference"}
                 and block.get("reason"), f"规则块排除无依据：{block.get('file')}:{block.get('start')}", errors)
    if not errors:
        for criterion in catalog['criteria']:
            expected = requirements_for(criterion['id'], coverage, root)
            need(expected and criterion.get('requirements') == expected,
                 f"{criterion['id']}子要求映射缺失或与原文不符", errors)
    return errors


def check_record(record, catalog, catalog_bytes, base, record_bytes=None, record_path=None):
    errors = []
    need(record.get("catalog_sha256") == digest(catalog_bytes), "记录绑定的规则版本不匹配", errors)
    for field in ("record_id", "revision", "date", "reviewer", "scope", "recoverable"):
        need(record.get(field), f"记录缺少{field}", errors)
    for value in (record.get("record_id"), record.get("date"), record.get("recoverable"),
                  record.get("reviewer", {}).get("name"), record.get("reviewer", {}).get("role"),
                  record.get("scope", {}).get("target")):
        need(value, "记录身份或范围为空白", errors)
        need(not str(value).startswith(("待填写", "待提交")), "记录身份或范围仍为占位内容", errors)
    need(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(record.get("date", ""))), "日期格式须为YYYY-MM-DD", errors)
    if record_bytes is not None:
        need(recover_data(record.get("recoverable"), base) == record_bytes, "记录自身受审全文不能恢复", errors)
    if record_path is not None and record.get("recoverable", {}).get("kind") == "snapshot":
        snapshot = base / record["recoverable"].get("path", "")
        need(snapshot.resolve() != record_path.resolve(), "恢复位置不能只是正在修改的记录自身", errors)
    criteria = {c["id"] for c in catalog["criteria"]}
    required = set(record.get("scope", {}).get("required_criteria", []))
    need(required and required <= criteria, "声明必查项为空或包含未知编号", errors)
    checks = record.get("checks", [])
    ids = [c.get("criterion_id") for c in checks]
    need(len(ids) == len(set(ids)) and set(ids) == criteria, "规则检查遗漏、重复或包含未知编号", errors)
    artifacts = record.get("artifacts", {})
    texts = {}
    for key, artifact in artifacts.items():
        path = base / artifact.get("path", "")
        if not need(path.is_file(), f"证据文件不存在：{key}", errors):
            continue
        raw = path.read_bytes()
        need(digest(raw) == artifact.get("sha256"), f"证据版本已变化：{key}", errors)
        need(artifact.get("version"), f"证据缺版本：{key}", errors)
        recovered = recover_data(artifact.get("recoverable"), base)
        need(recovered == raw, f"证据全文不能按登记位置恢复：{key}", errors)
        texts[key] = raw.decode("utf-8")
    targets = record.get("scope", {}).get("targets", [])
    target_ids = {t.get("artifact") for t in targets}
    need(targets, "范围未结构化绑定受审正文或记录", errors)
    for target in targets:
        actual = artifacts.get(target.get("artifact"), {})
        for field in ("path", "sha256", "version"):
            need(target.get(field) and target[field] == actual.get(field), f"范围目标{field}与实际证据不符", errors)
        need(target.get("range"), "范围目标缺实际阅读范围", errors)
        need(actual.get("kind") in {"source", "record"}, "范围目标必须绑定正文或受审记录", errors)

    def evidence(items, label):
        need(items, f"{label}缺少证据", errors)
        for item in items or []:
            need(item.get("quote"), f"{label}短引为空白", errors)
            need(item.get("artifact") in texts and item.get("quote")
                 and item["quote"] in texts.get(item.get("artifact"), ""), f"{label}证据短引无法定位", errors)
            need(item.get("locator"), f"{label}缺定位", errors)
            need(item.get("explanation"), f"{label}缺判断依据", errors)

    findings = record.get("findings", {})
    for key, finding in findings.items():
        status = finding.get("status")
        need(status in {"open", "changed", "recheck_failed", "closed", "withdrawn"}, f"{key}问题状态无效", errors)
        evidence(finding.get("before"), key + "原判断")
        if status == "closed":
            evidence(finding.get("after"), key + "实际修订")
            evidence(finding.get("reread", {}).get("evidence"), key + "上下文复读")
            before_id, after_id = finding.get("before_source"), finding.get("after_source")
            need(before_id in artifacts and after_id in artifacts
                 and artifacts.get(before_id, {}).get("kind") == artifacts.get(after_id, {}).get("kind") == "source"
                 and artifacts.get(before_id, {}).get("sha256") != artifacts.get(after_id, {}).get("sha256"),
                 f"{key}关闭项没有不同正文版本的修订证据", errors)
            need(finding.get("reread", {}).get("version") == artifacts.get(after_id, {}).get("version"),
                 f"{key}复读版本与修订正文版本不符", errors)
            need(any(e.get("artifact") == before_id for e in finding.get("before", [])), f"{key}原文证据未绑定改前正文", errors)
            need(any(e.get("artifact") == after_id for e in finding.get("after", [])), f"{key}修订证据未绑定改后正文", errors)
            need(any(e.get("artifact") == after_id for e in finding.get("reread", {}).get("evidence", [])),
                 f"{key}复读证据未绑定改后正文", errors)
        elif status == "withdrawn":
            evidence(finding.get("counterevidence"), key + "撤销反证")
            evidence(finding.get("reread", {}).get("evidence"), key + "撤销核验")
            original = finding.get("original_source")
            need(original in artifacts and artifacts.get(original, {}).get("kind") == "source", f"{key}撤销缺原正文对象", errors)
            need(any(e.get("artifact") == original for e in finding.get("counterevidence", []))
                 and any(e.get("artifact") == original for e in finding.get("reread", {}).get("evidence", [])),
                 f"{key}撤销证据未绑定原正文", errors)
            need(finding.get("reread", {}).get("version") == artifacts.get(original, {}).get("version"),
                 f"{key}撤销核验版本与原正文不符", errors)
        if status in {"closed", "withdrawn"}:
            reread = finding.get("reread", {})
            for field in ("reviewer", "version", "scope"):
                need(reread.get(field), f"{key}缺复读{field}", errors)
    for check in checks:
        label = str(check.get("criterion_id"))
        status = check.get("status")
        need(status in STATUSES, f"{label}状态无效", errors)
        need(check.get("reason"), f"{label}缺具体判断", errors)
        linked = check.get("findings", [])
        need(set(linked) <= set(findings), f"{label}引用未知问题", errors)
        if status in {"pass", "fail", "not_applicable", "out_of_scope"}:
            evidence(check.get("evidence"), label)
        if status in {"pass", "fail"}:
            need(check.get("units"), f"{label}缺实际检查单元", errors)
            need(check.get("performed_action"), f"{label}缺实际执行动作", errors)
        if status == "pending" and check.get("units"):
            need(check.get("performed_action"), f"{label}部分检查缺实际执行动作", errors)
            evidence(check.get("evidence"), label + "部分检查")
        criterion = next((c for c in catalog['criteria'] if c['id'] == check.get('criterion_id')), {})
        expected = {r['id'] for r in criterion.get('requirements', [])}
        subs = check.get('subchecks', [])
        sub_ids = [s.get('requirement_id') for s in subs]
        need(len(sub_ids) == len(set(sub_ids)) and set(sub_ids) <= expected, f"{label}子要求编号重复或未知", errors)
        for subcheck in subs:
            need(subcheck.get('status') in STATUSES, f"{label}子要求状态无效", errors)
            need(subcheck.get('reason'), f"{label}子要求缺判断依据", errors)
            if subcheck.get('status') in {'pass','fail','not_applicable','out_of_scope'}:
                need(subcheck.get('performed_action'), f"{label}子要求缺实际动作", errors)
                evidence(subcheck.get('evidence'), label + '子要求')
            if subcheck.get('status') == 'pass':
                need(subcheck.get('applicable_units') and set(subcheck['applicable_units']) == set(subcheck.get('units', []))
                     and len(subcheck.get('units', [])) == len(set(subcheck.get('units', []))),
                     f"{label}子要求缺完整适用单元核对", errors)
                need(any(e.get('artifact') in target_ids for e in subcheck.get('evidence', [])),
                     f"{label}子要求通过证据未绑定受审目标", errors)
            if subcheck.get('status') == 'pending':
                need(subcheck.get('missing'), f"{label}子要求未说明缺什么", errors)
                if subcheck.get('units'):
                    need(subcheck.get('performed_action'), f"{label}子要求部分检查缺实际动作", errors)
                    evidence(subcheck.get('evidence'), label + '子要求部分检查')
            if subcheck.get('status') == 'out_of_scope':
                need(subcheck.get('scope_basis'), f"{label}子要求范围外缺约定依据", errors)
        if status == "pass":
            need(any(e.get('artifact') in target_ids for e in check.get('evidence', [])),
                 f"{label}通过证据未绑定受审目标", errors)
            need(check.get("applicable_units") and set(check["applicable_units"]) == set(check.get("units", []))
                 and len(check.get("units", [])) == len(set(check.get("units", []))),
                 f"{label}局部检查不能冒充全部适用单元通过", errors)
            need(expected and {s.get('requirement_id') for s in subs} == expected and len(subs) == len(expected),
                 f"{label}未逐项核对所有子要求", errors)
            for subcheck in subs:
                need(subcheck.get('status') in {'pass','not_applicable'}, f"{label}子要求仍未通过", errors)
                need(subcheck.get('performed_action'), f"{label}子要求缺实际动作", errors)
                need(subcheck.get('reason'), f"{label}子要求缺判断依据", errors)
                evidence(subcheck.get('evidence'), label + '子要求')
        if status == "fail":
            need(linked, f"{label}未通过但没有问题编号", errors)
        if status == "pending":
            need(check.get("missing"), f"{label}未检查但未说明缺什么", errors)
        if status == "out_of_scope":
            need(check.get("scope_basis"), f"{label}范围外但未说明范围依据", errors)
        if status == "pass":
            need(all(findings[k].get("status") in {"closed", "withdrawn"} for k in linked if k in findings),
                 f"{label}仍有未解决问题却声称通过", errors)
    conclusions = record.get("conclusions", {})
    need(conclusions.get("record") in {"needs_review", "accepted", "needs_supplement", "unreliable"}, "缺有效记录结论", errors)
    need(conclusions.get("text") in {"needs_revision", "needs_reread", "passed", "insufficient_evidence"}, "缺有效正文结论", errors)
    if conclusions.get("record") == "accepted":
        evidence(record.get("audit", {}).get("evidence"), "记录接受结论")
        for field in ("reviewer", "scope"):
            need(record.get("audit", {}).get(field), f"缺记录复核{field}", errors)
    if conclusions.get("text") == "passed":
        active = [c for c in checks if c.get("criterion_id") in required]
        need(active and all(c.get("status") in {"pass", "not_applicable"} for c in active), "必查项仍未通过，不能验收正文", errors)
        need(all(f.get("status") in {"closed", "withdrawn"} for f in findings.values()), "正文问题仍未关闭", errors)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cat = sub.add_parser("catalog")
    cat.add_argument("--root", type=Path, required=True)
    cat.add_argument("--catalog", type=Path, required=True)
    init = sub.add_parser("init")
    init.add_argument("--catalog", type=Path, required=True)
    init.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("record")
    check.add_argument("--catalog", type=Path, required=True)
    check.add_argument("--record", type=Path, required=True)
    check.add_argument("--root", type=Path, required=True, help="对应规则全文的根目录；历史复核须使用相应历史版本")
    args = parser.parse_args()
    raw = args.catalog.read_bytes()
    catalog = json.loads(raw)
    if args.command == "catalog":
        errors = check_catalog(catalog, args.root)
    elif args.command == "init":
        if args.output.exists():
            parser.error("目标已存在；为避免覆盖受审记录，请使用新修订路径")
        record = {"schema_version": 1, "record_id": "待填写", "revision": "R1", "date": "待填写",
                  "catalog_sha256": digest(raw), "reviewer": {"name": "待填写", "role": "待填写"},
                  "recoverable": {"kind":"snapshot", "path":"待填写受审快照路径"},
                  "scope": {"target": "待填写", "targets":[], "required_criteria": [c["id"] for c in catalog["criteria"]]},
                  "artifacts": {}, "findings": {}, "checks": [],
                  "conclusions": {"record": "needs_review", "text": "insufficient_evidence"}}
        for c in catalog["criteria"]:
            record["checks"].append({"criterion_id": c["id"], "status": "pending", "units": [], "applicable_units": [], "performed_action": "",
                                     "reason": "尚未执行", "missing": "缺原文核对及具体判断依据", "evidence": [], "findings": [],
                                     "subchecks":[{'requirement_id':r['id'],'status':'pending','reason':'尚未核对原文子要求',
                                                   'missing':'缺实际动作、定位证据及具体判断'} for r in c.get('requirements',[])]})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("已生成待填写记录；没有预设通过或不适用结论。")
        return 0
    else:
        errors = check_catalog(catalog, args.root) + check_record(read_json(args.record), catalog, raw, args.record.parent, args.record.read_bytes(), args.record)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("结构核对通过；不代表阅读判断正确或正文通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
