"""CLI helpers for the snapshot pipeline (exporter_v2)."""
from __future__ import annotations

import argparse
from typing import Optional

from tab_export.exporter_v2 import SnapshotOptions, SnapshotResult
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.filter import FilterOptions


def add_snapshot_args(parser: argparse.ArgumentParser) -> None:
    """Register snapshot-related CLI arguments onto *parser*."""
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        default=False,
        help="Disable duplicate removal in the snapshot pipeline.",
    )
    parser.add_argument(
        "--sort-by",
        choices=[k.value for k in SortKey],
        default=None,
        help="Sort tabs by this field before output.",
    )
    parser.add_argument(
        "--sort-order",
        choices=[o.value for o in SortOrder],
        default="asc",
        help="Sort direction (asc or desc).",
    )
    parser.add_argument(
        "--keyword",
        default=None,
        help="Filter: keep only tabs whose title or URL contains this keyword.",
    )
    parser.add_argument(
        "--diff-against",
        default=None,
        metavar="FILE",
        help="Path to a previous export file to diff against.",
    )


def build_snapshot_options(args: argparse.Namespace) -> SnapshotOptions:
    """Build a SnapshotOptions from parsed CLI args."""
    sort: Optional[SortOptions] = None
    if getattr(args, "sort_by", None):
        sort = SortOptions(
            key=SortKey(args.sort_by),
            order=SortOrder(args.sort_order),
        )

    filter_opts: Optional[FilterOptions] = None
    if getattr(args, "keyword", None):
        filter_opts = FilterOptions(keyword=args.keyword)

    return SnapshotOptions(
        deduplicate=not getattr(args, "no_dedup", False),
        sort=sort,
        filter=filter_opts,
        output_format=getattr(args, "format", "markdown"),
    )


def render_snapshot_summary(result: SnapshotResult) -> str:
    """Return a human-readable summary of the snapshot result."""
    lines = [
        "Snapshot summary",
        f"  Tabs before : {result.tabs_before}",
        f"  Tabs after  : {result.tabs_after}",
        f"  Duplicates  : {result.removed_duplicates}",
        f"  Filtered out: {result.filtered_out}",
    ]
    if result.diff is not None:
        lines.append(f"  Diff added  : {result.diff.added_count}")
        lines.append(f"  Diff removed: {result.diff.removed_count}")
    return "\n".join(lines)
