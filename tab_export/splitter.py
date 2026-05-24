"""Split a TabExport into multiple exports based on a maximum tab count per chunk."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from tab_export.parser import Tab, TabExport


@dataclass
class SplitResult:
    """Result of splitting a TabExport into chunks."""

    chunks: List[TabExport] = field(default_factory=list)

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    @property
    def chunk_sizes(self) -> List[int]:
        return [
            sum(len(tabs) for tabs in chunk.export.values())
            for chunk in self.chunks
        ]


def split_export(export: TabExport, max_tabs: int) -> SplitResult:
    """Split *export* into chunks where each chunk has at most *max_tabs* tabs.

    Groups are never broken across chunks: a group is placed into the current
    chunk if it fits entirely; otherwise a new chunk is started.  If a single
    group contains more tabs than *max_tabs* it is placed alone in its own
    chunk.

    Args:
        export: The source :class:`TabExport` to split.
        max_tabs: Maximum number of tabs allowed per chunk (must be >= 1).

    Returns:
        A :class:`SplitResult` containing the list of chunk exports.
    """
    if max_tabs < 1:
        raise ValueError("max_tabs must be at least 1")

    chunks: List[TabExport] = []
    current: dict[str, List[Tab]] = {}
    current_count = 0

    for group in export.groups():
        group_tabs: List[Tab] = list(export.tabs_in_group(group))
        group_size = len(group_tabs)

        if current_count + group_size > max_tabs and current:
            chunks.append(TabExport(export=dict(current), source_file=export.source_file))
            current = {}
            current_count = 0

        current[group] = group_tabs
        current_count += group_size

    if current:
        chunks.append(TabExport(export=dict(current), source_file=export.source_file))

    return SplitResult(chunks=chunks)
