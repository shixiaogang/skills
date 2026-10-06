#!/usr/bin/env python3
"""Compile a standalone TikZ source and convert it to requested formats."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

SUPPORTED_FORMATS = ("pdf", "svg", "png")
AUXILIARY_SUFFIXES = (
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".xdv",
)


class CompileError(RuntimeError):
    pass


def executable(name: str) -> Optional[str]:
    return shutil.which(name)


def parse_formats(raw: str) -> List[str]:
    formats = []
    for item in raw.split(","):
        value = item.strip().lower()
        if not value:
            continue
        if value not in SUPPORTED_FORMATS:
            supported = ", ".join(SUPPORTED_FORMATS)
            raise argparse.ArgumentTypeError(
                f"Unsupported format '{value}'. Choose from: {supported}"
            )
        if value not in formats:
            formats.append(value)
    if not formats:
        raise argparse.ArgumentTypeError("At least one output format is required")
    return formats


def choose_engine(requested: str) -> str:
    if requested != "auto":
        if executable(requested):
            return requested
        raise CompileError(f"Requested TeX engine not found: {requested}")

    for candidate in ("xelatex", "lualatex", "pdflatex"):
        if executable(candidate):
            return candidate
    raise CompileError(
        "No TeX engine found. Install XeLaTeX, LuaLaTeX, or pdfLaTeX; "
        "XeLaTeX is recommended for Chinese labels."
    )


def run_command(command: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def compile_pdf(source: Path, output_dir: Path, engine: str) -> Path:
    latexmk = executable("latexmk")
    if latexmk:
        engine_flag = {
            "xelatex": "-xelatex",
            "lualatex": "-lualatex",
            "pdflatex": "-pdf",
        }[engine]
        command = [
            latexmk,
            engine_flag,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={output_dir}",
            source.name,
        ]
    else:
        engine_path = executable(engine)
        if not engine_path:
            raise CompileError(f"TeX engine not found: {engine}")
        command = [
            engine_path,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-output-directory={output_dir}",
            source.name,
        ]

    result = run_command(command, source.parent)
    log_path = output_dir / f"{source.stem}.compile.log"
    log_path.write_text(
        "$ " + " ".join(command) + "\n\n" + result.stdout + result.stderr,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise CompileError(
            f"TikZ compilation failed with exit code {result.returncode}. "
            f"See {log_path}"
        )

    pdf = output_dir / f"{source.stem}.pdf"
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise CompileError(
            f"TeX engine reported success but PDF was not created: {pdf}"
        )
    return pdf


def convert_svg(pdf: Path, output: Path) -> None:
    pdf2svg = executable("pdf2svg")
    dvisvgm = executable("dvisvgm")
    if pdf2svg:
        result = run_command([pdf2svg, str(pdf), str(output)], pdf.parent)
    elif dvisvgm:
        result = run_command(
            [
                dvisvgm,
                "--pdf",
                "--page=1",
                f"--output={output}",
                str(pdf),
            ],
            pdf.parent,
        )
    else:
        raise CompileError(
            "SVG requested but no converter found. Install pdf2svg or dvisvgm."
        )

    if result.returncode != 0 or not output.is_file():
        raise CompileError(f"SVG conversion failed: {result.stderr.strip()}")


def convert_png(pdf: Path, output: Path, dpi: int) -> None:
    pdftocairo = executable("pdftocairo")
    pdftoppm = executable("pdftoppm")
    magick = executable("magick")
    if pdftocairo:
        prefix = output.with_suffix("")
        result = run_command(
            [
                pdftocairo,
                "-png",
                "-singlefile",
                "-r",
                str(dpi),
                str(pdf),
                str(prefix),
            ],
            pdf.parent,
        )
    elif pdftoppm:
        prefix = output.with_suffix("")
        result = run_command(
            [pdftoppm, "-png", "-singlefile", "-r", str(dpi), str(pdf), str(prefix)],
            pdf.parent,
        )
    elif magick:
        result = run_command(
            [
                magick,
                "-density",
                str(dpi),
                f"{pdf}[0]",
                str(output),
            ],
            pdf.parent,
        )
    else:
        raise CompileError(
            "PNG requested but no converter found. Install Poppler or ImageMagick."
        )

    if result.returncode != 0 or not output.is_file():
        raise CompileError(f"PNG conversion failed: {result.stderr.strip()}")


def clean_auxiliary_files(output_dir: Path, stem: str) -> None:
    for suffix in AUXILIARY_SUFFIXES:
        candidate = output_dir / f"{stem}{suffix}"
        if candidate.exists():
            candidate.unlink()


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile standalone TikZ to PDF and optional SVG/PNG outputs."
    )
    parser.add_argument("source", type=Path, help="TikZ .tex source")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory; defaults to the source directory",
    )
    parser.add_argument(
        "--formats",
        type=parse_formats,
        default=parse_formats("pdf,svg,png"),
        help="Comma-separated subset of pdf,svg,png",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "xelatex", "lualatex", "pdflatex"),
        default="auto",
    )
    parser.add_argument("--dpi", type=int, default=300, help="PNG resolution")
    parser.add_argument(
        "--keep-build",
        action="store_true",
        help="Keep TeX auxiliary files",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    source = args.source.expanduser().resolve()

    if not source.is_file():
        print(f"Source file not found: {source}", file=sys.stderr)
        return 2
    if source.suffix.lower() != ".tex":
        print(f"Expected a .tex source file: {source}", file=sys.stderr)
        return 2
    if args.dpi <= 0:
        print("--dpi must be positive", file=sys.stderr)
        return 2

    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else source.parent
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        engine = choose_engine(args.engine)
        pdf = compile_pdf(source, output_dir, engine)
        generated = [pdf]
        errors = []
        if "svg" in args.formats:
            svg = output_dir / f"{source.stem}.svg"
            try:
                convert_svg(pdf, svg)
                generated.append(svg)
            except CompileError as exc:
                errors.append(f"SVG: {exc}")
        if "png" in args.formats:
            png = output_dir / f"{source.stem}.png"
            try:
                convert_png(pdf, png, args.dpi)
                generated.append(png)
            except CompileError as exc:
                errors.append(f"PNG: {exc}")

        requested = set(args.formats)
        for output in generated:
            if output.suffix.lstrip(".") in requested:
                print(f"PASS {output}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 3 if errors else 0
    except CompileError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    finally:
        if not args.keep_build:
            clean_auxiliary_files(output_dir, source.stem)


if __name__ == "__main__":
    raise SystemExit(main())
