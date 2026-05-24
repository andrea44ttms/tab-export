"""CLI helpers for the merge feature."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from tab_export.merger import MergeResult, merge_exports
from tab_export.parser import TabExport, parse


def add_merger_args(parser: argparse.ArgumentParser) -> None:
    """Register merge-related arguments on *parser*."""
    parser.add_argument(
        "--merge",
        metavar="FILE",
        dest="merge_files",
        action="append",
        default=[],
        help=(
            "Path to an additional tab-export file to merge into the primary "
            "input.  May be specified multiple times."
        ),
    )
    parser.add_argument(
        "--no-dedup-merge",
        dest="merge_dedup",
        action="store_false",
        default=True,
        help="Allow duplicate URLs when merging (default: deduplicate).",
    )
    parser.add_argument(
        "--show-merge-summary",
        dest="show_merge_summary",
        action="store_true",
        default=False,
        help="Print a merge summary to stderr after processing.",
    )


def apply_merges(
    base: TabExport,
    args: argparse.Namespace,
) -> TabExport:
    """Apply any --merge files to *base* and return the combined export.

    If ``args.show_merge_summary`` is True, each merge summary is written to
    *stderr*.  Returns *base* unchanged when no merge files are specified.
    """
    merge_files: List[str] = getattr(args, "merge_files", [])
    if not merge_files:
        return base

    deduplicate: bool = getattr(args, "merge_dedup", True)
    show_summary: bool = getattr(args, "show_merge_summary", False)

    current = base
    for filepath in merge_files:
        path = Path(filepath)
        if not path.exists():
            print(f"[merge] Warning: file not found: {filepath}", file=sys.stderr)
            continue

        incoming = parse(path)
        result: MergeResult = merge_exports(
            current, incoming, deduplicate=deduplicate
        )
        if show_summary:
            print(f"[merge] {result.summary}", file=sys.stderr)
        current = result.export

    return current
