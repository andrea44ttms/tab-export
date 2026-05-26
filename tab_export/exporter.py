"""Exporter module for tab export."""

from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import TabExport
from tab_export.deduplicator import deduplicate
from tab_export.sorter import SortOptions, sort_export
from tab_export.filter import FilterOptions, filter_export
from tab_export.formatter import format_export


@dataclass
class PipelineOptions:
    deduplicate: bool = True
    sort: Optional[SortOptions] = None
    filter: Optional[FilterOptions] = None
    output_format: str = "markdown"


@dataclass
class PipelineResult:
    output: str
    tabs_before: int
    tabs_after: int
    duplicates_removed: int
    tabs_filtered: int

    @property
    def tabs_removed(self) -> int:
        return self.duplicates_removed + self.tabs_filtered


def _count_tabs(export: TabExport) -> int:
    return sum(len(list(export.tabs_in_group(g))) for g in export.groups())


def run_pipeline(export: TabExport, options: Optional[PipelineOptions] = None) -> PipelineResult:
    if options is None:
        options = PipelineOptions()

    tabs_before = _count_tabs(export)
    duplicates_removed = 0
    tabs_filtered = 0

    if options.deduplicate:
        dedup_result = deduplicate(export)
        export = dedup_result.export
        duplicates_removed = dedup_result.removed_count

    if options.filter is not None:
        filter_result = filter_export(export, options.filter)
        tabs_filtered = filter_result.removed_count
        export = filter_result.export

    if options.sort is not None:
        export = sort_export(export, options.sort)

    output = format_export(export, options.output_format)
    tabs_after = _count_tabs(export)

    return PipelineResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        duplicates_removed=duplicates_removed,
        tabs_filtered=tabs_filtered,
    )
