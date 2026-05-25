"""High-level pipeline runner that chains filter, sort, dedup, and truncate steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import TabExport
from tab_export.filter import FilterOptions, filter_export
from tab_export.sorter import SortOptions, sort_export
from tab_export.deduplicator import deduplicate
from tab_export.truncator import TruncateOptions, truncate_export
from tab_export.formatter import format_export


@dataclass
class FullPipelineOptions:
    filter_opts: Optional[FilterOptions] = None
    sort_opts: Optional[SortOptions] = None
    deduplicate: bool = True
    truncate_opts: Optional[TruncateOptions] = None
    output_format: str = "markdown"


@dataclass
class FullPipelineResult:
    output: str
    tabs_before: int = 0
    tabs_after: int = 0
    removed_duplicates: int = 0
    was_truncated: bool = False
    steps_applied: list[str] = field(default_factory=list)

    @property
    def tabs_removed_by_filter(self) -> int:
        return self.tabs_before - self.tabs_after - self.removed_duplicates


def _count_tabs(export: TabExport) -> int:
    return sum(len(tabs) for tabs in export.tabs_in_group.values())


def run_full_pipeline(
    export: TabExport,
    options: Optional[FullPipelineOptions] = None,
) -> FullPipelineResult:
    """Run the full processing pipeline and return formatted output."""
    if options is None:
        options = FullPipelineOptions()

    steps: list[str] = []
    tabs_before = _count_tabs(export)
    current = export
    removed_duplicates = 0
    was_truncated = False

    if options.filter_opts is not None:
        result = filter_export(current, options.filter_opts)
        current = result.export
        steps.append("filter")

    if options.sort_opts is not None:
        result = sort_export(current, options.sort_opts)
        current = result.export
        steps.append("sort")

    if options.deduplicate:
        result = deduplicate(current)
        removed_duplicates = result.removed_count
        current = result.export
        steps.append("deduplicate")

    if options.truncate_opts is not None:
        result = truncate_export(current, options.truncate_opts)
        was_truncated = result.was_truncated
        current = result.export
        steps.append("truncate")

    tabs_after = _count_tabs(current)
    output = format_export(current, fmt=options.output_format)

    return FullPipelineResult(
        output=output,
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        removed_duplicates=removed_duplicates,
        was_truncated=was_truncated,
        steps_applied=steps,
    )
