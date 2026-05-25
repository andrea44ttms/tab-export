"""CLI helpers for the tab prioritizer."""
from __future__ import annotations

import argparse
from typing import List

from tab_export.parser import TabExport
from tab_export.prioritizer import PriorityRule, PrioritizingResult, prioritize_export


def add_prioritizer_args(parser: argparse.ArgumentParser) -> None:
    """Register prioritizer arguments on *parser*."""
    parser.add_argument(
        "--prioritize",
        metavar="FIELD:KEYWORD:LEVEL",
        action="append",
        dest="priority_rules",
        default=[],
        help=(
            "Add a priority rule. Format: title:python:10 or url:github.com:8. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--show-top",
        metavar="N",
        type=int,
        default=0,
        dest="show_top_n",
        help="Print the top-N prioritized tabs after processing.",
    )


def _parse_priority_rules(raw: List[str]) -> List[PriorityRule]:
    rules: List[PriorityRule] = []
    for token in raw:
        parts = token.split(":", 2)
        if len(parts) != 3:
            raise ValueError(
                f"Invalid priority rule {token!r}. Expected FIELD:KEYWORD:LEVEL."
            )
        field, keyword, level_str = parts
        if field not in ("title", "url"):
            raise ValueError(f"Field must be 'title' or 'url', got {field!r}.")
        rules.append(PriorityRule(keyword=keyword, field=field, priority=int(level_str)))
    return rules


def apply_prioritizing(
    export: TabExport,
    args: argparse.Namespace,
) -> PrioritizingResult:
    """Run prioritization based on parsed CLI *args*."""
    rules = _parse_priority_rules(getattr(args, "priority_rules", []))
    return prioritize_export(export, rules)


def render_priority_summary(result: PrioritizingResult, top_n: int = 0) -> str:
    """Return a human-readable summary of prioritization results."""
    lines = [
        "=== Priority Summary ===",
        f"Tabs prioritized : {result.total_prioritized}",
    ]
    if top_n > 0:
        lines.append(f"\nTop {top_n} tabs:")
        for tab in result.top_tabs(n=top_n):
            pri = result.priority_for(tab)
            lines.append(f"  [{pri:>3}] {tab.title}  <{tab.url}>")
    return "\n".join(lines) + "\n"
