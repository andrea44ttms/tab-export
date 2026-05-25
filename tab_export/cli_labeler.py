"""CLI helpers for the labeler feature."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from tab_export.labeler import LabelRule, LabelingResult, label_export
from tab_export.parser import TabExport


def add_labeler_args(parser: argparse.ArgumentParser) -> None:
    """Register labeler-related CLI arguments."""
    parser.add_argument(
        "--label-rules",
        metavar="FILE",
        help="JSON file containing label rules (list of objects with label, keyword, url_contains, title_contains)",
    )
    parser.add_argument(
        "--show-labels",
        action="store_true",
        help="Print a summary of labels applied to tabs",
    )


def load_label_rules(path: str) -> List[LabelRule]:
    """Load label rules from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rules: List[LabelRule] = []
    for entry in data:
        rules.append(
            LabelRule(
                label=entry["label"],
                keyword=entry.get("keyword"),
                url_contains=entry.get("url_contains"),
                title_contains=entry.get("title_contains"),
            )
        )
    return rules


def render_label_summary(result: LabelingResult) -> str:
    """Return a human-readable summary of labeling results."""
    lines = ["## Label Summary", f"Tabs labeled: {result.total_labeled}"]
    for url, labels in sorted(result.label_map.items()):
        lines.append(f"  {url} -> {', '.join(labels)}")
    return "\n".join(lines)


def apply_labeling(export: TabExport, args: argparse.Namespace) -> LabelingResult | None:
    """Run labeling if --label-rules is provided; return result or None."""
    if not getattr(args, "label_rules", None):
        return None
    rules = load_label_rules(args.label_rules)
    return label_export(export, rules)
