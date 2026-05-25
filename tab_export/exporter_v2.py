"""Tab export pipeline v2 with snapshot and diff support."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import TabExport
from tab_export.deduplicator import deduplicate
from tab_export.sorter import SortOptions, sort_export
from tab_export.filter import FilterOptions, filter_export
from tab_export.formatter import format_export
from tab_export.differ import diff_exports, DiffResult


@dataclass
class SnapshotOptions:
    deduplicate: bool = True
    sort: Optional[SortOptions] = None
    filter: Optional[FilterOptions] = None
    output_format: str = "markdown"
    previous: Optional[TabExport] = None


@dataclass
class SnapshotResult:
    output: str
    tabs_before: int
    tabs_after: int
    removed_duplicates: int
    filtered_out: int
    diff: Optional[DiffResult] = None

    @property
    def tabs_removed(self) -> int:
        return self.tabs_before - self.tabs_after

    @property
    def has_diff(self) -> bool:
        return self.diff is not None and self.diff.has_changes


def _count_tabs(export: TabExport) -> int:
    return sum(len(tabs) for tabs in export.groups.values())


def run_snapshot(export: TabExport, options: Optional[SnapshotOptions] = None) -> SnapshotResult:
    """Run a snapshot pipeline: dedup, filter, sort, format, and optionally diff."""
    if options is None:
        options = SnapshotOptions()

    tabs_before = _count_tabs(export)
    removed_duplicates = 0
    filtered_out = 0

    current = export

    if options.deduplicate:
        dedup_result = deduplicate(current)
        current = dedup_result.export
        removed_duplicates = dedup_result.removed_count

    if options.filter is not None:
        filter_result = filter_export(current, options.filter)
        filtered_out = filter_result.removed_count
        current = filter_result.export

    if options.sort is not None:
        current = sort_export(current, options.sort)

    tabs_after = _count_tabs(current)
    output = format_export(current, fmt=options.output_format)

    diff: Optional[DiffResult] = None
    if options.previous is not None:
        diff = diff_exports(options.previous, current)

    return SnapshotResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        removed_duplicates=removed_duplicates,
        filtered_out=filtered_out,
        diff=diff,
    )
