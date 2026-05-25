"""CLI helpers for the colorizer feature."""
from __future__ import annotations

import argparse
from typing import List

from tab_export.colorizer import ColorRule, ColorizingResult, colorize_export, render_colorized_text
from tab_export.parser import TabExport


def add_colorizer_args(parser: argparse.ArgumentParser) -> None:
    """Register colorizer-related CLI arguments onto *parser*."""
    parser.add_argument(
        "--colorize",
        metavar="KEYWORD:COLOR",
        action="append",
        default=[],
        help=(
            "Colorize tabs whose title contains KEYWORD with COLOR. "
            "Valid colors: red, green, yellow, blue, magenta, cyan. "
            "Can be repeated."
        ),
    )
    parser.add_argument(
        "--colorize-field",
        choices=["title", "url", "both"],
        default="title",
        help="Which field to match against for --colorize rules (default: title).",
    )
    parser.add_argument(
        "--show-colors",
        action="store_true",
        default=False,
        help="Print a colorized summary after processing.",
    )


def _parse_color_rules(raw: List[str], match_field: str) -> List[ColorRule]:
    """Parse ``KEYWORD:COLOR`` strings into :class:`ColorRule` objects."""
    rules: List[ColorRule] = []
    for entry in raw:
        if ":" not in entry:
            continue
        keyword, _, color = entry.partition(":")
        keyword = keyword.strip()
        color = color.strip().lower()
        if keyword and color:
            rules.append(ColorRule(keyword=keyword, color=color, match_field=match_field))
    return rules


def apply_colorizing(
    export: TabExport,
    args: argparse.Namespace,
) -> ColorizingResult:
    """Run the colorizer pipeline stage based on parsed CLI *args*."""
    rules = _parse_color_rules(
        getattr(args, "colorize", []) or [],
        getattr(args, "colorize_field", "title"),
    )
    return colorize_export(export, rules)


def render_color_summary(result: ColorizingResult) -> str:
    """Return a human-readable summary of colorization results."""
    lines = ["=== Colorization Summary ==="]
    lines.append(f"Total tabs colorized : {result.total_colorized}")
    if result.color_map:
        lines.append("")
        lines.append("Colored tabs:")
        for url, color in sorted(result.color_map.items()):
            lines.append(f"  [{color}] {url}")
    return "\n".join(lines)
