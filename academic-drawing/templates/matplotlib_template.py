#!/usr/bin/env python3
"""Copy and rename this file before adapting it to a specific figure."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

MM_PER_INCH = 25.4

OKABE_ITO = [
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#D55E00",
    "#CC79A7",
    "#56B4E9",
    "#000000",
]
MARKERS = ["o", "s", "^", "D", "v", "P", "X"]
LINESTYLES = ["-", "--", ":", "-."]


def mm_to_inches(value: float) -> float:
    return value / MM_PER_INCH


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Arial",
                "Helvetica",
                "Noto Sans CJK SC",
                "DejaVu Sans",
            ],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.linewidth": 0.7,
            "axes.prop_cycle": cycler(color=OKABE_ITO),
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "legend.fontsize": 7,
            "lines.linewidth": 1.0,
            "lines.markersize": 5.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def load_rows(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV file has no header")
        rows = list(reader)

    if not rows:
        raise ValueError("CSV file has no data rows")
    return rows


def parse_number(row: Dict[str, str], key: str, row_number: int) -> float:
    if key not in row:
        available = ", ".join(row)
        raise KeyError(f"Column '{key}' not found. Available columns: {available}")

    raw = row[key].strip()
    if not raw:
        raise ValueError(f"Missing value in column '{key}' at CSV row {row_number}")

    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            f"Non-numeric value {raw!r} in column '{key}' at CSV row {row_number}"
        ) from exc
    if not math.isfinite(value):
        raise ValueError(
            f"Non-finite value {raw!r} in column '{key}' at CSV row {row_number}"
        )
    return value


def group_points(
    rows: Sequence[Dict[str, str]],
    x_key: str,
    y_key: str,
    group_key: Optional[str],
    sort_x: bool,
) -> List[Tuple[str, List[float], List[float]]]:
    grouped: Dict[str, Tuple[List[float], List[float]]] = {}

    for row_number, row in enumerate(rows, start=2):
        group = row.get(group_key, "").strip() if group_key else "Data"
        if group_key and not group:
            raise ValueError(
                f"Missing value in group column '{group_key}' at CSV row {row_number}"
            )
        x_value = parse_number(row, x_key, row_number)
        y_value = parse_number(row, y_key, row_number)
        xs, ys = grouped.setdefault(group, ([], []))
        xs.append(x_value)
        ys.append(y_value)

    if len(grouped) > len(OKABE_ITO):
        raise ValueError(
            f"{len(grouped)} groups exceed the line-safe template palette. "
            "Use direct labels, facets, or a documented accessible palette."
        )

    result = []
    for group, (xs, ys) in grouped.items():
        points = list(zip(xs, ys))
        if sort_x:
            points.sort(key=lambda point: point[0])
        result.append(
            (
                group,
                [point[0] for point in points],
                [point[1] for point in points],
            )
        )
    return result


def build_figure(
    groups: Iterable[Tuple[str, List[float], List[float]]],
    width_mm: float,
    height_mm: float,
    x_label: str,
    y_label: str,
    title: Optional[str],
    plot_type: str,
):
    configure_style()
    fig, ax = plt.subplots(
        figsize=(mm_to_inches(width_mm), mm_to_inches(height_mm)),
        constrained_layout=True,
    )

    plotted = 0
    for index, (label, xs, ys) in enumerate(groups):
        color = OKABE_ITO[index]
        marker = MARKERS[index]
        if plot_type == "line":
            ax.plot(
                xs,
                ys,
                color=color,
                label=label,
                marker=marker,
                linestyle=LINESTYLES[index % len(LINESTYLES)],
                markerfacecolor="white",
                markeredgewidth=0.8,
                markevery=max(1, len(xs) // 20),
            )
        else:
            ax.scatter(
                xs,
                ys,
                s=22,
                label=label,
                marker=marker,
                facecolors="none",
                edgecolors=color,
                linewidths=0.8,
            )
        plotted += 1

    if not plotted:
        raise ValueError("No validated data series to plot")

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title, fontsize=9, fontweight="bold")
    if plotted > 1:
        ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig


def save_figure(fig, output_prefix: Path, dpi: int) -> List[Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for suffix, options in (
        (".pdf", {}),
        (".svg", {}),
        (".png", {"dpi": dpi}),
    ):
        output = output_prefix.with_suffix(suffix)
        fig.savefig(output, facecolor="white", **options)
        outputs.append(output)
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adaptable publication figure template for numeric CSV data."
    )
    parser.add_argument("--data", type=Path, required=True, help="Input CSV file")
    parser.add_argument("--x", required=True, help="Numeric x-axis column")
    parser.add_argument("--y", required=True, help="Numeric y-axis column")
    parser.add_argument("--group", help="Optional categorical grouping column")
    parser.add_argument("--x-label", required=True, help="X-axis label with units")
    parser.add_argument("--y-label", required=True, help="Y-axis label with units")
    parser.add_argument("--title", help="Optional concise in-figure title")
    parser.add_argument(
        "--plot-type",
        choices=("scatter", "line"),
        default="scatter",
        help="Use line only when the x-axis has a verified order",
    )
    parser.add_argument(
        "--sort-x",
        action="store_true",
        help="Stably sort each line by x; ignored for scatter",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        required=True,
        help="Output path without an extension",
    )
    parser.add_argument("--width-mm", type=float, default=90.0)
    parser.add_argument("--height-mm", type=float, default=60.0)
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.width_mm <= 0 or args.height_mm <= 0 or args.dpi <= 0:
        raise ValueError("Figure dimensions and DPI must be positive")
    rows = load_rows(args.data)
    groups = group_points(
        rows,
        args.x,
        args.y,
        args.group,
        sort_x=args.sort_x and args.plot_type == "line",
    )
    figure = build_figure(
        groups,
        args.width_mm,
        args.height_mm,
        args.x_label,
        args.y_label,
        args.title,
        args.plot_type,
    )
    outputs = save_figure(figure, args.output_prefix, args.dpi)
    plt.close(figure)
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
