"""Export pipeline: combines filter, sort, deduplicate, and format steps."""

from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import TabExport
from tab_export.filter import FilterOptions, filter_export
from tab_export.sorter import SortOptions, sort_export
from tab_export.deduplicator import deduplicate
from tab_export.formatter import format_export
from tab_export.stats import compute_stats
from tab_export.reporter import render_stats_text


@dataclass
class PipelineOptions:
    filter_opts: Optional[FilterOptions] = None
    sort_opts: Optional[SortOptions] = None
    deduplicate: bool = False
    output_format: str = "markdown"  # "markdown" or "notion"
    include_stats: bool = False


@dataclass
class PipelineResult:
    output: str
    stats_report: Optional[str] = None
    removed_duplicates: int = 0
    filtered_out: int = 0


def run_pipeline(export: TabExport, opts: PipelineOptions) -> PipelineResult:
    """Run the full export pipeline and return formatted output."""
    removed_duplicates = 0
    filtered_out = 0

    current = export

    if opts.filter_opts is not None:
        result = filter_export(current, opts.filter_opts)
        current = result.export
        filtered_out = result.removed_count

    if opts.deduplicate:
        dedup_result = deduplicate(current)
        current = dedup_result.export
        removed_duplicates = dedup_result.removed_count

    if opts.sort_opts is not None:
        current = sort_export(current, opts.sort_opts)

    output = format_export(current, fmt=opts.output_format)

    stats_report: Optional[str] = None
    if opts.include_stats:
        stats = compute_stats(current)
        stats_report = render_stats_text(stats)

    return PipelineResult(
        output=output,
        stats_report=stats_report,
        removed_duplicates=removed_duplicates,
        filtered_out=filtered_out,
    )
