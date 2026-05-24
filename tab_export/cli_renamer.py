"""CLI helpers for the tab renamer feature."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from tab_export.renamer import RenameRule, RenamingResult


def add_renamer_args(parser: argparse.ArgumentParser) -> None:
    """Register renamer-related arguments onto *parser*."""
    parser.add_argument(
        "--rename",
        metavar="FIND:REPLACE",
        action="append",
        default=[],
        help="Simple find-and-replace rule applied to tab titles (repeatable).",
    )
    parser.add_argument(
        "--rename-regex",
        metavar="PATTERN:REPLACE",
        action="append",
        default=[],
        help="Regex find-and-replace rule applied to tab titles (repeatable).",
    )
    parser.add_argument(
        "--rename-rules-file",
        metavar="FILE",
        default=None,
        help="JSON file containing an array of rename rule objects.",
    )
    parser.add_argument(
        "--rename-case-sensitive",
        action="store_true",
        default=False,
        help="Make --rename rules case-sensitive (default: case-insensitive).",
    )


def load_rename_rules(args: argparse.Namespace) -> List[RenameRule]:
    """Build a list of RenameRule objects from parsed CLI arguments."""
    rules: List[RenameRule] = []
    case_sensitive = getattr(args, "rename_case_sensitive", False)

    for spec in getattr(args, "rename", []) or []:
        if ":" not in spec:
            continue
        find, _, replace = spec.partition(":")
        rules.append(RenameRule(pattern=find, replacement=replace, case_sensitive=case_sensitive))

    for spec in getattr(args, "rename_regex", []) or []:
        if ":" not in spec:
            continue
        pattern, _, replace = spec.partition(":")
        rules.append(RenameRule(pattern=pattern, replacement=replace, use_regex=True, case_sensitive=case_sensitive))

    rules_file = getattr(args, "rename_rules_file", None)
    if rules_file:
        data = json.loads(Path(rules_file).read_text(encoding="utf-8"))
        for entry in data:
            rules.append(
                RenameRule(
                    pattern=entry["pattern"],
                    replacement=entry["replacement"],
                    use_regex=entry.get("use_regex", False),
                    case_sensitive=entry.get("case_sensitive", True),
                )
            )

    return rules


def render_rename_summary(result: RenamingResult) -> str:
    """Return a human-readable summary of the renaming result."""
    lines = [
        "=== Rename Summary ===",
        f"Tabs renamed : {result.total_renamed}",
    ]
    return "\n".join(lines) + "\n"
