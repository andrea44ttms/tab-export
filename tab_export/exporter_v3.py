"""Batch export pipeline: process multiple input files into a single merged output."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from tab_export.parser import TabExport, parse
from tab_export.merger import merge_exports
from tab_export.deduplicator import deduplicate
from tab_export.formatter import format_export


@dataclass
class BatchOptions:
    input_files: List[Path]
    fmt: str = "markdown"          # "markdown" | "notion"
    deduplicate_across: bool = True
    label: Optional[str] = None    # optional top-level label for merged export


@dataclass
class BatchResult:
    output: str
    files_processed: int
    tabs_before: int
    tabs_after: int
    duplicates_removed: int

    @property
    def was_deduplicated(self) -> bool:
        return self.duplicates_removed > 0

    def summary(self) -> str:
        lines = [
            f"Files processed : {self.files_processed}",
            f"Tabs before     : {self.tabs_before}",
            f"Duplicates      : {self.duplicates_removed}",
            f"Tabs after      : {self.tabs_after}",
        ]
        return "\n".join(lines)


def _count_tabs(export: TabExport) -> int:
    return sum(len(tabs) for tabs in export.tabs_in_group.values())


def run_batch(options: BatchOptions) -> BatchResult:
    """Parse every input file, merge them, optionally deduplicate, then format."""
    if not options.input_files:
        raise ValueError("At least one input file is required.")

    exports: List[TabExport] = [parse(p) for p in options.input_files]

    merged = exports[0]
    for incoming in exports[1:]:
        from tab_export.merger import MergeResult
        result = merge_exports(merged, incoming)
        merged = result.merged

    tabs_before = _count_tabs(merged)
    duplicates_removed = 0

    if options.deduplicate_across:
        dedup_result = deduplicate(merged)
        merged = dedup_result.export
        duplicates_removed = dedup_result.removed_count

    tabs_after = _count_tabs(merged)
    output = format_export(merged, fmt=options.fmt)

    return BatchResult(
        output=output,
        files_processed=len(options.input_files),
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        duplicates_removed=duplicates_removed,
    )
