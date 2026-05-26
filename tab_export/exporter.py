"""Tab export pipeline orchestration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import TabExport
from tab_export.deduplicator import deduplicate
from tab_export.sorter import SortOptions, sort_export
from tab_export.filter import FilterOptions, filter_export
from tab_export.formatter import format_export


@dataclass
class PipelineOptions:
    output_format: str = "markdown"
    deduplicate: bool = True
    sort: Optional[SortOptions] = None
    filter: Optional[FilterOptions] = None


@dataclass
class PipelineResult:
    output: str
    tabs_before: int
    tabs_after: int
    duplicates_removed: int
    tabs_filtered: int
    _options: PipelineOptions = field(repr=False, default_factory=PipelineOptions)


def run_pipeline(export: TabExport, options: Optional[PipelineOptions] = None) -> PipelineResult:
    """Run the full export pipeline and return a PipelineResult."""
    if options is None:
        options = PipelineOptions()

    tabs_before = sum(len(g.tabs) for g in export.groups())
    duplicates_removed = 0
    tabs_filtered = 0

    current = export

    if options.deduplicate:
        dedup_result = deduplicate(current)
        current = dedup_result.export
        duplicates_removed = dedup_result.removed_count

    if options.filter is not None:
        filter_result = filter_export(current, options.filter)
        current = filter_result.export
        tabs_filtered = filter_result.removed_count

    if options.sort is not None:
        current = sort_export(current, options.sort)

    output = format_export(current, fmt=options.output_format)
    tabs_after = sum(len(g.tabs) for g in current.groups())

    return PipelineResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        duplicates_removed=duplicates_removed,
        tabs_filtered=tabs_filtered,
        _options=options,
    )
