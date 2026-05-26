"""Export pipeline: applies deduplication, sorting, filtering, and formatting."""
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
    _removed: int = field(init=False)

    def __post_init__(self) -> None:
        self._removed = self.tabs_before - self.tabs_after

    @property
    def tabs_removed(self) -> int:
        return self._removed


def _count_tabs(export: TabExport) -> int:
    return sum(len(tabs) for tabs in export.tabs_in_group.values())


def run_pipeline(export: TabExport, options: Optional[PipelineOptions] = None) -> PipelineResult:
    """Run the full processing pipeline on a TabExport and return formatted output."""
    if options is None:
        options = PipelineOptions()

    tabs_before = _count_tabs(export)
    current = export

    if options.filter is not None:
        filter_result = filter_export(current, options.filter)
        current = filter_result.export

    if options.deduplicate:
        dedup_result = deduplicate(current)
        current = dedup_result.export

    if options.sort is not None:
        sort_result = sort_export(current, options.sort)
        current = sort_result

    tabs_after = _count_tabs(current)
    output = format_export(current, fmt=options.output_format)

    return PipelineResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
    )
