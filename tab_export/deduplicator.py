"""Deduplication utilities for tab exports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from tab_export.parser import Tab, TabExport


@dataclass
class DeduplicationResult:
    """Result of a deduplication pass."""

    export: TabExport
    removed: List[Tab] = field(default_factory=list)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def deduplicate(export: TabExport, *, across_groups: bool = True) -> DeduplicationResult:
    """Remove duplicate tabs from a TabExport.

    Args:
        export: The parsed tab export to deduplicate.
        across_groups: When True (default), a URL seen in any previous group
            is considered a duplicate.  When False, duplicates are only
            removed within each group independently.

    Returns:
        A :class:`DeduplicationResult` containing the cleaned export and the
        list of tabs that were removed.
    """
    seen_globally: set[str] = set()
    removed: list[Tab] = []
    new_groups: dict[str, list[Tab]] = {}

    for group_name in export.groups:
        seen_in_group: set[str] = set()
        clean_tabs: list[Tab] = []

        for tab in export.tabs_in_group(group_name):
            url = tab.url
            scope = seen_globally if across_groups else seen_in_group

            if url in scope:
                removed.append(tab)
            else:
                clean_tabs.append(tab)
                seen_in_group.add(url)
                seen_globally.add(url)

        new_groups[group_name] = clean_tabs

    # Rebuild a TabExport with deduplicated tabs
    all_clean_tabs: list[Tab] = []
    for tabs in new_groups.values():
        all_clean_tabs.extend(tabs)

    clean_export = TabExport(
        tabs=all_clean_tabs,
        source_file=export.source_file,
    )
    return DeduplicationResult(export=clean_export, removed=removed)
