"""Pipeline orchestrator that wires together core processing steps."""
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
    deduplicate: bool = True
    sort: Optional[SortOptions] = None
    filter: Optional[FilterOptions] = None
    output_format: str = "markdown"  # "markdown" | "notion"

    def __post_init__(self) -> None:
        if self.output_format not in ("markdown", "notion"):
            raise ValueError(f"Unknown output_format: {self.output_format!r}")


@dataclass
class PipelineResult:
    output: str
    tabs_before: int
    tabs_after: int
    tabs_removed: int = field(init=False)
    dedup_removed: int = 0
    filter_removed: int = 0

    def __post_init__(self) -> None:
        self.tabs_removed = self.tabs_before - self.tabs_after


def _count_tabs(export: TabExport) -> int:
    return sum(len(tabs) for tabs in export.tabs_in_group.values())


def run_pipeline(export: TabExport, options: Optional[PipelineOptions] = None) -> PipelineResult:
    """Run the standard processing pipeline and return formatted output."""
    if options is None:
        options = PipelineOptions()

    tabs_before = _count_tabs(export)
    dedup_removed = 0
    filter_removed = 0

    if options.deduplicate:
        dedup_result = deduplicate(export)
        export = dedup_result.export
        dedup_removed = dedup_result.removed_count

    if options.filter is not None:
        filter_result = filter_export(export, options.filter)
        export = filter_result.export
        filter_removed = filter_result.removed_count

    if options.sort is not None:
        export = sort_export(export, options.sort)

    output = format_export(export, fmt=options.output_format)
    tabs_after = _count_tabs(export)

    return PipelineResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        dedup_removed=dedup_removed,
        filter_removed=filter_removed,
    )
