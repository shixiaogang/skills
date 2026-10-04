#!/usr/bin/env python3
"""Validate technical properties of academic figure outputs."""

from __future__ import annotations

import argparse
import ast
import binascii
import json
import math
import re
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
MAX_PNG_PIXELS = 100_000_000
MAX_PNG_RAW_BYTES = 512 * 1024 * 1024
WHITE_NAMES = {"white", "#fff", "#ffffff", "rgb(255,255,255)"}


def issue(level: str, message: str) -> Dict[str, str]:
    return {"level": level, "message": message}


def parse_length_mm(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    match = re.fullmatch(
        r"\s*([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|in|pt|px)?\s*",
        value,
        re.IGNORECASE,
    )
    if not match:
        return None
    number = float(match.group(1))
    unit = (match.group(2) or "px").lower()
    factors = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
        "pt": 25.4 / 72.0,
        "px": 25.4 / 96.0,
    }
    return number * factors[unit]


def paeth(left: int, above: int, upper_left: int) -> int:
    prediction = left + above - upper_left
    distance_left = abs(prediction - left)
    distance_above = abs(prediction - above)
    distance_upper_left = abs(prediction - upper_left)
    if distance_left <= distance_above and distance_left <= distance_upper_left:
        return left
    if distance_above <= distance_upper_left:
        return above
    return upper_left


def unfilter_png_rows(
    raw: bytes,
    width: int,
    height: int,
    bytes_per_pixel: int,
) -> List[bytes]:
    row_length = width * bytes_per_pixel
    expected = height * (row_length + 1)
    if len(raw) != expected:
        raise ValueError(
            f"decompressed PNG data has {len(raw)} bytes; expected {expected}"
        )

    rows = []
    previous = bytearray(row_length)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        encoded = raw[offset : offset + row_length]
        offset += row_length
        decoded = bytearray(row_length)

        for index, byte in enumerate(encoded):
            left = decoded[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = (
                previous[index - bytes_per_pixel]
                if index >= bytes_per_pixel
                else 0
            )
            if filter_type == 0:
                value = byte
            elif filter_type == 1:
                value = byte + left
            elif filter_type == 2:
                value = byte + above
            elif filter_type == 3:
                value = byte + ((left + above) // 2)
            elif filter_type == 4:
                value = byte + paeth(left, above, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter type: {filter_type}")
            decoded[index] = value & 0xFF

        rows.append(bytes(decoded))
        previous = decoded
    return rows


def visible_rgb_values(
    rows: Iterable[bytes],
    color_type: int,
    palette: Optional[bytes],
    transparency: Optional[bytes],
) -> Iterable[Tuple[int, int, int]]:
    def composite(channel: int, alpha: int) -> int:
        return round((channel * alpha + 255 * (255 - alpha)) / 255)

    for row in rows:
        channels = PNG_CHANNELS[color_type]
        for offset in range(0, len(row), channels):
            pixel = row[offset : offset + channels]
            if color_type == 0:
                yield (pixel[0], pixel[0], pixel[0])
            elif color_type == 2:
                yield (pixel[0], pixel[1], pixel[2])
            elif color_type == 3:
                index = pixel[0]
                alpha = (
                    transparency[index]
                    if transparency and index < len(transparency)
                    else 255
                )
                if not palette or index * 3 + 2 >= len(palette):
                    raise ValueError("indexed PNG is missing a valid palette")
                red, green, blue = palette[index * 3 : index * 3 + 3]
                yield (
                    composite(red, alpha),
                    composite(green, alpha),
                    composite(blue, alpha),
                )
            elif color_type == 4:
                value, alpha = pixel
                composited = composite(value, alpha)
                yield (composited, composited, composited)
            elif color_type == 6:
                red, green, blue, alpha = pixel
                yield (
                    composite(red, alpha),
                    composite(green, alpha),
                    composite(blue, alpha),
                )


def validate_png(
    path: Path,
    min_dpi: float,
    require_dpi: bool,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        return [issue("FAIL", "invalid PNG signature")]

    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    dpi_x = dpi_y = None
    palette = transparency = None
    compressed = bytearray()

    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            return [issue("FAIL", "PNG is truncated inside a chunk")]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(
            ">I", data[offset + 8 + length : offset + 12 + length]
        )[0]
        actual_crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            return [issue("FAIL", f"PNG chunk {kind!r} has an invalid CRC")]
        offset += 12 + length

        if kind == b"IHDR":
            if len(payload) != 13:
                return [issue("FAIL", "PNG IHDR chunk has an invalid length")]
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif kind == b"pHYs" and len(payload) == 9:
            pixels_x, pixels_y, unit = struct.unpack(">IIB", payload)
            if unit == 1:
                dpi_x = pixels_x * 0.0254
                dpi_y = pixels_y * 0.0254
        elif kind == b"PLTE":
            palette = payload
        elif kind == b"tRNS":
            transparency = payload
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break

    if not width or not height or color_type not in PNG_CHANNELS:
        return [issue("FAIL", "PNG has unsupported or missing image metadata")]
    if color_type == 3:
        if not palette:
            return [issue("FAIL", "indexed PNG is missing a palette")]
        if len(palette) % 3 != 0 or len(palette) // 3 > 2**bit_depth:
            return [issue("FAIL", "indexed PNG has an invalid palette")]

    findings.append(issue("PASS", f"PNG dimensions {width}x{height} px"))
    channels = PNG_CHANNELS[color_type]
    expected_raw_bytes = height * (width * channels + 1)
    if (
        width * height > MAX_PNG_PIXELS
        or expected_raw_bytes > MAX_PNG_RAW_BYTES
    ):
        findings.append(
            issue(
                "FAIL",
                "PNG exceeds validator resource limit "
                f"({MAX_PNG_PIXELS:,} pixels or {MAX_PNG_RAW_BYTES:,} raw bytes)",
            )
        )
        return findings

    if dpi_x and dpi_y:
        findings.append(issue("PASS", f"PNG resolution {dpi_x:.1f}x{dpi_y:.1f} dpi"))
        if min(dpi_x, dpi_y) + 0.5 < min_dpi:
            findings.append(
                issue("FAIL", f"PNG resolution is below required {min_dpi:g} dpi")
            )
        width_mm = width / dpi_x * 25.4
        height_mm = height / dpi_y * 25.4
        findings.extend(
            compare_size(
                width_mm,
                height_mm,
                expected_width_mm,
                expected_height_mm,
                tolerance_mm,
            )
        )
    elif require_dpi:
        findings.append(issue("FAIL", "PNG has no physical DPI metadata"))
    else:
        findings.append(issue("WARN", "PNG has no physical DPI metadata"))

    if bit_depth != 8 or interlace != 0:
        findings.append(
            issue(
                "WARN",
                "blank-image check skipped for non-8-bit or interlaced PNG",
            )
        )
        return findings

    try:
        decompressor = zlib.decompressobj()
        raw = decompressor.decompress(bytes(compressed), expected_raw_bytes + 1)
        if decompressor.unconsumed_tail or len(raw) > expected_raw_bytes:
            raise ValueError("decompressed PNG data exceeds declared image size")
        raw += decompressor.flush(expected_raw_bytes + 1 - len(raw))
        if len(raw) > expected_raw_bytes:
            raise ValueError("decompressed PNG data exceeds declared image size")
        rows = unfilter_png_rows(raw, width, height, channels)
    except (ValueError, zlib.error) as exc:
        findings.append(issue("FAIL", f"PNG pixel decoding failed: {exc}"))
        return findings

    minimum = [255, 255, 255]
    maximum = [0, 0, 0]
    pixel_count = 0
    try:
        for pixel in visible_rgb_values(rows, color_type, palette, transparency):
            pixel_count += 1
            for channel in range(3):
                minimum[channel] = min(minimum[channel], pixel[channel])
                maximum[channel] = max(maximum[channel], pixel[channel])
    except ValueError as exc:
        findings.append(issue("FAIL", f"PNG pixel decoding failed: {exc}"))
        return findings
    if pixel_count == 0:
        findings.append(issue("FAIL", "PNG contains no decodable pixels"))
        return findings

    channel_ranges = [
        maximum[channel] - minimum[channel] for channel in range(3)
    ]
    if max(channel_ranges) <= 2:
        findings.append(issue("FAIL", "PNG appears blank or single-color"))
    else:
        findings.append(issue("PASS", "PNG contains visible tonal variation"))
    return findings


def compare_size(
    width_mm: float,
    height_mm: float,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    findings = [issue("PASS", f"physical size {width_mm:.2f}x{height_mm:.2f} mm")]
    width_mismatch = (
        expected_width_mm is not None
        and abs(width_mm - expected_width_mm) > tolerance_mm
    )
    if width_mismatch:
        findings.append(
            issue(
                "FAIL",
                f"width {width_mm:.2f} mm differs from expected "
                f"{expected_width_mm:.2f} mm",
            )
        )
    height_mismatch = (
        expected_height_mm is not None
        and abs(height_mm - expected_height_mm) > tolerance_mm
    )
    if height_mismatch:
        findings.append(
            issue(
                "FAIL",
                f"height {height_mm:.2f} mm differs from expected "
                f"{expected_height_mm:.2f} mm",
            )
        )
    return findings


def parse_svg_style(element: ET.Element, inherited: Dict[str, str]) -> Dict[str, str]:
    style = dict(inherited)
    for name in (
        "display",
        "visibility",
        "opacity",
        "fill",
        "fill-opacity",
        "stroke",
        "stroke-opacity",
    ):
        if name in element.attrib:
            style[name] = element.attrib[name].strip().lower()
    for declaration in element.attrib.get("style", "").split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        style[name.strip().lower()] = value.strip().lower()
    return style


def opacity_is_visible(style: Dict[str, str], key: str) -> bool:
    try:
        value = style.get(key, "1")
        if value.endswith("%"):
            return float(value[:-1]) > 0
        return float(value) > 0
    except ValueError:
        return True


def svg_element_is_painted(
    tag: str,
    element: ET.Element,
    style: Dict[str, str],
    element_ids: set,
) -> bool:
    if not opacity_is_visible(style, "opacity"):
        return False

    fill = style.get("fill", "black")
    stroke = style.get("stroke", "none")
    fill_visible = fill != "none" and opacity_is_visible(style, "fill-opacity")
    stroke_visible = stroke != "none" and opacity_is_visible(style, "stroke-opacity")

    if tag in {"line", "polyline"}:
        return stroke_visible
    if tag == "text":
        return bool("".join(element.itertext()).strip()) and (
            stroke_visible or (fill_visible and fill not in WHITE_NAMES)
        )
    if tag == "image":
        return any(
            name.endswith("href") and bool(value.strip())
            for name, value in element.attrib.items()
        )
    if tag == "use":
        href = next(
            (
                value.strip()
                for name, value in element.attrib.items()
                if name.endswith("href")
            ),
            "",
        )
        if not href:
            return False
        return not href.startswith("#") or href[1:] in element_ids
    if tag == "path" and not element.attrib.get("d", "").strip():
        return False
    if tag == "polygon" and not element.attrib.get("points", "").strip():
        return False
    if tag in {"path", "polygon", "circle", "ellipse", "rect"}:
        if stroke_visible:
            return True
        return fill_visible and fill not in WHITE_NAMES
    return False


def svg_has_visible_content(root: ET.Element) -> bool:
    excluded = {"defs", "clipPath", "mask", "metadata", "style", "symbol"}
    graphics = {
        "path",
        "line",
        "polyline",
        "polygon",
        "circle",
        "ellipse",
        "rect",
        "text",
        "image",
        "use",
    }
    element_ids = {
        element_id
        for element in root.iter()
        if (element_id := element.attrib.get("id"))
    }

    def visit(
        element: ET.Element,
        inherited: Dict[str, str],
        hidden: bool,
    ) -> bool:
        tag = element.tag.split("}")[-1]
        if tag in excluded:
            return False
        style = parse_svg_style(element, inherited)
        hidden = hidden or style.get("display") == "none"
        hidden = hidden or style.get("visibility") in {"hidden", "collapse"}
        hidden = hidden or not opacity_is_visible(style, "opacity")
        if hidden:
            return False
        if tag in graphics and svg_element_is_painted(
            tag,
            element,
            style,
            element_ids,
        ):
            return True
        return any(visit(child, style, hidden) for child in element)

    return visit(root, {}, False)


def validate_svg(
    path: Path,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [issue("FAIL", f"invalid SVG XML: {exc}")]

    if root.tag.split("}")[-1] != "svg":
        return [issue("FAIL", "root element is not svg")]

    findings: List[Dict[str, str]] = []
    view_box = root.attrib.get("viewBox")
    if not view_box:
        findings.append(issue("FAIL", "SVG has no viewBox"))
    else:
        parts = view_box.replace(",", " ").split()
        if len(parts) != 4:
            findings.append(issue("FAIL", "SVG viewBox must contain four numbers"))
        else:
            try:
                if float(parts[2]) <= 0 or float(parts[3]) <= 0:
                    raise ValueError
                findings.append(issue("PASS", f"SVG viewBox {view_box}"))
            except ValueError:
                findings.append(issue("FAIL", "SVG viewBox has invalid dimensions"))

    width_mm = parse_length_mm(root.attrib.get("width"))
    height_mm = parse_length_mm(root.attrib.get("height"))
    if width_mm is None or height_mm is None:
        findings.append(issue("WARN", "SVG has no parseable physical size"))
    else:
        findings.extend(
            compare_size(
                width_mm,
                height_mm,
                expected_width_mm,
                expected_height_mm,
                tolerance_mm,
            )
        )

    if svg_has_visible_content(root):
        findings.append(issue("PASS", "SVG contains visible content elements"))
    else:
        findings.append(issue("FAIL", "SVG appears blank"))
    return findings


def pdf_with_fitz(
    path: Path,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    try:
        import fitz
    except ImportError:
        return []

    findings: List[Dict[str, str]] = []
    try:
        document = fitz.open(path)
    except Exception as exc:
        return [issue("FAIL", f"invalid PDF: {exc}")]

    try:
        if document.page_count != 1:
            findings.append(
                issue("FAIL", f"figure PDF has {document.page_count} pages; expected 1")
            )
            if document.page_count == 0:
                return findings
        else:
            findings.append(issue("PASS", "PDF has one page"))

        page = document[0]
        width_mm = page.rect.width * 25.4 / 72.0
        height_mm = page.rect.height * 25.4 / 72.0
        findings.extend(
            compare_size(
                width_mm,
                height_mm,
                expected_width_mm,
                expected_height_mm,
                tolerance_mm,
            )
        )

        pixmap = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), alpha=False)
        samples = pixmap.samples
        if not samples or max(samples) - min(samples) <= 2:
            findings.append(issue("FAIL", "PDF appears blank or single-color"))
        else:
            findings.append(issue("PASS", "PDF contains visible tonal variation"))

        fonts = page.get_fonts(full=True)
        if not fonts:
            findings.append(issue("WARN", "PDF contains no detectable text fonts"))
        else:
            unembedded = []
            for font in fonts:
                xref = font[0]
                try:
                    extracted = document.extract_font(xref)
                    font_bytes = extracted[3] if len(extracted) > 3 else b""
                except Exception:
                    font_bytes = b""
                if not font_bytes:
                    unembedded.append(font[3] or font[2] or str(xref))
            if unembedded:
                findings.append(
                    issue(
                        "WARN",
                        "possibly unembedded PDF fonts: " + ", ".join(unembedded),
                    )
                )
            else:
                findings.append(issue("PASS", "PDF fonts appear embedded"))
    finally:
        document.close()
    return findings


def pdf_with_pdfinfo(
    path: Path,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return [
            issue(
                "WARN",
                "PDF deep checks skipped; install PyMuPDF or pdfinfo",
            )
        ]
    result = subprocess.run(
        [pdfinfo, str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [issue("FAIL", f"invalid PDF: {result.stderr.strip()}")]

    findings = [issue("PASS", "PDF metadata is readable")]
    pages_match = re.search(r"^Pages:\s*(\d+)\s*$", result.stdout, re.MULTILINE)
    if not pages_match:
        findings.append(issue("WARN", "pdfinfo did not report a page count"))
    else:
        pages = int(pages_match.group(1))
        if pages != 1:
            findings.append(
                issue("FAIL", f"figure PDF has {pages} pages; expected 1")
            )
        else:
            findings.append(issue("PASS", "PDF has one page"))

    match = re.search(
        r"Page size:\s*([0-9.]+)\s+x\s+([0-9.]+)\s+pts",
        result.stdout,
    )
    if match:
        findings.extend(
            compare_size(
                float(match.group(1)) * 25.4 / 72.0,
                float(match.group(2)) * 25.4 / 72.0,
                expected_width_mm,
                expected_height_mm,
                tolerance_mm,
            )
        )

    pdffonts = shutil.which("pdffonts")
    if not pdffonts:
        findings.append(issue("WARN", "pdffonts unavailable; font check skipped"))
        return findings

    font_result = subprocess.run(
        [pdffonts, str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if font_result.returncode != 0:
        findings.append(issue("WARN", "pdffonts could not inspect the PDF"))
        return findings

    font_lines = font_result.stdout.splitlines()[2:]
    embedded = []
    for line in font_lines:
        match = re.search(
            r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$",
            line,
        )
        if match:
            embedded.append(match.group(1) == "yes")
    if not font_lines:
        findings.append(issue("WARN", "PDF contains no detectable text fonts"))
    elif not embedded:
        findings.append(issue("WARN", "pdffonts output could not be parsed"))
    elif all(embedded):
        findings.append(issue("PASS", "PDF fonts appear embedded"))
    else:
        findings.append(issue("WARN", "PDF contains possibly unembedded fonts"))
    return findings


def validate_pdf(
    path: Path,
    expected_width_mm: Optional[float],
    expected_height_mm: Optional[float],
    tolerance_mm: float,
) -> List[Dict[str, str]]:
    findings = pdf_with_fitz(
        path,
        expected_width_mm,
        expected_height_mm,
        tolerance_mm,
    )
    if findings:
        return findings
    return pdf_with_pdfinfo(
        path,
        expected_width_mm,
        expected_height_mm,
        tolerance_mm,
    )


def validate_source(path: Path) -> List[Dict[str, str]]:
    if path.suffix.lower() == ".tex":
        text = path.read_text(encoding="utf-8")
        if "\\begin{tikzpicture}" not in text:
            return [issue("FAIL", "TeX source has no tikzpicture environment")]
        return [issue("PASS", "TikZ source is present")]
    if path.suffix.lower() == ".py":
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            return [issue("FAIL", f"invalid Python source: {exc}")]
        return [issue("PASS", "Python source parses successfully")]
    return [issue("PASS", "file is non-empty")]


def validate_file(
    path: Path,
    args: argparse.Namespace,
) -> List[Dict[str, str]]:
    if not path.is_file():
        return [issue("FAIL", "file not found")]
    if path.stat().st_size == 0:
        return [issue("FAIL", "file is empty")]

    suffix = path.suffix.lower()
    if suffix == ".png":
        return validate_png(
            path,
            args.min_dpi,
            args.require_dpi,
            args.expected_width_mm,
            args.expected_height_mm,
            args.tolerance_mm,
        )
    if suffix == ".svg":
        return validate_svg(
            path,
            args.expected_width_mm,
            args.expected_height_mm,
            args.tolerance_mm,
        )
    if suffix == ".pdf":
        return validate_pdf(
            path,
            args.expected_width_mm,
            args.expected_height_mm,
            args.tolerance_mm,
        )
    return validate_source(path)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate academic figure source and output files."
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--min-dpi", type=float, default=300.0)
    parser.add_argument("--require-dpi", action="store_true")
    parser.add_argument("--expected-width-mm", type=float)
    parser.add_argument("--expected-height-mm", type=float)
    parser.add_argument("--tolerance-mm", type=float, default=1.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.min_dpi <= 0 or args.tolerance_mm < 0:
        print(
            "ERROR: --min-dpi must be positive and tolerance non-negative",
            file=sys.stderr,
        )
        return 2
    for value, name in (
        (args.expected_width_mm, "--expected-width-mm"),
        (args.expected_height_mm, "--expected-height-mm"),
    ):
        if value is not None and (not math.isfinite(value) or value <= 0):
            print(f"ERROR: {name} must be a positive finite number", file=sys.stderr)
            return 2

    report = []
    has_failures = False
    for raw_path in args.files:
        path = raw_path.expanduser().resolve()
        findings = validate_file(path, args)
        if any(item["level"] == "FAIL" for item in findings):
            has_failures = True
        report.append({"path": str(path), "findings": findings})

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report:
            print(item["path"])
            for finding in item["findings"]:
                print(f"  {finding['level']}: {finding['message']}")
    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
