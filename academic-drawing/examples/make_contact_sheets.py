"""Compose a contact sheet per examples/ category.

Each subdirectory of examples/ becomes one PNG grid, used by index.md as a
quick overview before readers click into individual references.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

EXAMPLES_DIR = Path(__file__).resolve().parent
CATEGORIES = ["architecture", "flow", "comparison", "neural-network"]

TILE_W = 760
TILE_H = 520
LABEL_H = 60
PAD = 28
COLS = 3
BG = (255, 255, 255)
LABEL_FG = (15, 23, 42)
LABEL_BG = (241, 245, 249)

try:
    FONT = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22
    )
except OSError:
    FONT = ImageFont.load_default()


def paste_tile(sheet, draw, img_path: Path, col: int, row: int) -> None:
    x0 = PAD + col * (TILE_W + PAD)
    y0 = PAD + row * (TILE_H + LABEL_H + PAD)
    tile = Image.open(img_path).convert("RGB")
    tile.thumbnail((TILE_W, TILE_H), Image.LANCZOS)
    tx = x0 + (TILE_W - tile.width) // 2
    ty = y0 + (TILE_H - tile.height) // 2
    sheet.paste(tile, (tx, ty))
    label_rect = (x0, y0 + TILE_H, x0 + TILE_W, y0 + TILE_H + LABEL_H)
    draw.rectangle(label_rect, fill=LABEL_BG)
    label = img_path.stem.replace("-", " ")
    bbox = draw.textbbox((0, 0), label, font=FONT)
    tx = x0 + (TILE_W - (bbox[2] - bbox[0])) // 2
    ty = y0 + TILE_H + (LABEL_H - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((tx, ty), label, fill=LABEL_FG, font=FONT)


def build_sheet(category: str) -> dict:
    src = EXAMPLES_DIR / category
    paths = sorted(src.glob("*.png"))
    # skip contact sheets themselves
    paths = [p for p in paths if not p.name.startswith("contact-sheet")]
    if not paths:
        return {"category": category, "skipped": "no images"}
    rows = (len(paths) + COLS - 1) // COLS
    w = COLS * TILE_W + (COLS + 1) * PAD
    h = rows * (TILE_H + LABEL_H) + (rows + 1) * PAD
    sheet = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(sheet)
    for idx, p in enumerate(paths):
        paste_tile(sheet, draw, p, idx % COLS, idx // COLS)
    out = src / "contact-sheet.png"
    sheet.save(out, optimize=True)
    print(f"saved {out} ({w}x{h})")
    return {"category": category, "size": [w, h], "items": [p.stem for p in paths]}


def main() -> None:
    manifest = {"sheets": [build_sheet(c) for c in CATEGORIES]}
    (EXAMPLES_DIR / "contact-sheet.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
