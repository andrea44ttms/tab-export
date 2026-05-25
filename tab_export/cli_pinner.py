"""CLI helpers for the pinning feature."""
from __future__ import annotations

import argparse
from typing import List

from tab_export.parser import TabExport
from tab_export.pinner import PinRule, PinningResult, pin_export


def add_pinner_args(parser: argparse.ArgumentParser) -> None:
    """Register pin-related arguments onto *parser*."""
    parser.add_argument(
        "--pin",
        metavar="KEYWORD",
        action="append",
        dest="pin_keywords",
        default=[],
        help="Pin tabs whose title or URL contains KEYWORD (repeatable).",
    )
    parser.add_argument(
        "--pin-field",
        choices=["title", "url", "both"],
        default="both",
        dest="pin_field",
        help="Which field to match pin keywords against (default: both).",
    )
    parser.add_argument(
        "--pin-marker",
        default="📌",
        dest="pin_marker",
        help="Marker prepended to pinned tab titles (default: 📌).",
    )
    parser.add_argument(
        "--show-pinned",
        action="store_true",
        default=False,
        dest="show_pinned",
        help="Print a summary of pinned tabs after processing.",
    )


def apply_pinning(
    export: TabExport,
    args: argparse.Namespace,
) -> tuple[TabExport, PinningResult | None]:
    """Run the pinning pipeline step if any pin keywords were supplied.

    Returns the (possibly updated) export and the :class:`PinningResult`, or
    ``None`` when no pinning was requested.
    """
    keywords: List[str] = getattr(args, "pin_keywords", [])
    if not keywords:
        return export, None

    field = getattr(args, "pin_field", "both")
    marker = getattr(args, "pin_marker", "📌")
    rules = [PinRule(keyword=kw, match_field=field) for kw in keywords]
    result = pin_export(export, rules=rules, pin_marker=marker)
    return result.export, result


def render_pin_summary(result: PinningResult) -> str:
    """Return a human-readable summary of the pinning result."""
    lines = [f"Pinned tabs: {result.total_pinned}"]
    for url in result.pinned_urls:
        lines.append(f"  {url}")
    return "\n".join(lines)
