"""CLI helpers for the annotation feature."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from tab_export.annotator import AnnotationResult, AnnotationRule


def add_annotator_args(parser: argparse.ArgumentParser) -> None:
    """Register annotation-related arguments onto *parser*."""
    parser.add_argument(
        "--annotate",
        metavar="RULES_JSON",
        default=None,
        help=(
            "Path to a JSON file containing annotation rules. "
            "Each rule is an object with 'note' and optionally "
            "'url_contains' / 'title_contains'."
        ),
    )
    parser.add_argument(
        "--show-annotations",
        action="store_true",
        default=False,
        help="Print annotation summary after processing.",
    )


def load_rules(path: str) -> List[AnnotationRule]:
    """Load annotation rules from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rules: List[AnnotationRule] = []
    for item in data:
        rules.append(
            AnnotationRule(
                note=item["note"],
                url_contains=item.get("url_contains"),
                title_contains=item.get("title_contains"),
            )
        )
    return rules


def render_annotation_summary(result: AnnotationResult) -> str:
    """Return a human-readable summary of applied annotations."""
    lines = [f"Annotations applied: {result.total_annotated}"]
    for url, note in result.annotations.items():
        lines.append(f"  [{note}] {url}")
    return "\n".join(lines)
