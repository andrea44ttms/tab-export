"""Compare two TabExport snapshots and report differences."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from tab_export.parser import Tab, TabExport


@dataclass
class ComparisonResult:
    """Result of comparing two TabExport snapshots."""

    added_tabs: List[Tab] = field(default_factory=list)
    removed_tabs: List[Tab] = field(default_factory=list)
    added_groups: List[str] = field(default_factory=list)
    removed_groups: List[str] = field(default_factory=list)

    @property
    def total_added(self) -> int:
        return len(self.added_tabs)

    @property
    def total_removed(self) -> int:
        return len(self.removed_tabs)

    @property
    def is_unchanged(self) -> bool:
        return (
            not self.added_tabs
            and not self.removed_tabs
            and not self.added_groups
            and not self.removed_groups
        )

    def summary_lines(self) -> List[str]:
        lines: List[str] = []
        lines.append(f"Added tabs:   {self.total_added}")
        lines.append(f"Removed tabs: {self.total_removed}")
        if self.added_groups:
            lines.append("New groups:   " + ", ".join(self.added_groups))
        if self.removed_groups:
            lines.append("Gone groups:  " + ", ".join(self.removed_groups))
        return lines


def _tab_key(tab: Tab) -> Tuple[str, str]:
    """Unique identity for a tab based on URL and title."""
    return (tab.url.strip(), tab.title.strip())


def compare_exports(before: TabExport, after: TabExport) -> ComparisonResult:
    """Return a ComparisonResult describing what changed between two exports."""
    before_keys: Set[Tuple[str, str]] = set()
    after_keys: Set[Tuple[str, str]] = set()

    before_tabs_by_key = {_tab_key(t): t for g in before.groups() for t in before.tabs_in_group(g)}
    after_tabs_by_key = {_tab_key(t): t for g in after.groups() for t in after.tabs_in_group(g)}

    before_keys = set(before_tabs_by_key)
    after_keys = set(after_tabs_by_key)

    added_tabs = [after_tabs_by_key[k] for k in sorted(after_keys - before_keys)]
    removed_tabs = [before_tabs_by_key[k] for k in sorted(before_keys - after_keys)]

    before_groups = set(before.groups())
    after_groups = set(after.groups())

    added_groups = sorted(after_groups - before_groups)
    removed_groups = sorted(before_groups - after_groups)

    return ComparisonResult(
        added_tabs=added_tabs,
        removed_tabs=removed_tabs,
        added_groups=added_groups,
        removed_groups=removed_groups,
    )
