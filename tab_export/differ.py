"""Generates human-readable diffs between two TabExport snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from tab_export.parser import Tab, TabExport


@dataclass
class DiffResult:
    """Holds the line-by-line diff output and summary metadata."""

    lines: List[str] = field(default_factory=list)
    added_count: int = 0
    removed_count: int = 0
    unchanged_count: int = 0

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def has_changes(self) -> bool:
        return self.added_count > 0 or self.removed_count > 0

    def summary(self) -> str:
        return (
            f"+{self.added_count} added, "
            f"-{self.removed_count} removed, "
            f"{self.unchanged_count} unchanged"
        )


def _tab_key(tab: Tab) -> str:
    """Canonical identity key for a tab."""
    return tab.url.strip()


def _all_urls(export: TabExport) -> Set[str]:
    return {_tab_key(t) for group in export.groups for t in export.tabs_in_group(group)}


def diff_exports(before: TabExport, after: TabExport) -> DiffResult:
    """Produce a unified-style diff between *before* and *after*.

    Groups present in either snapshot are shown.  Within each group tabs
    are marked with '+' (added), '-' (removed), or ' ' (unchanged).
    """
    result = DiffResult()

    before_urls = _all_urls(before)
    after_urls = _all_urls(after)

    all_groups: List[str] = list(
        dict.fromkeys(list(before.groups) + list(after.groups))
    )

    for group in all_groups:
        before_tabs = {_tab_key(t): t for t in before.tabs_in_group(group)}
        after_tabs = {_tab_key(t): t for t in after.tabs_in_group(group)}

        all_keys = list(dict.fromkeys(list(before_tabs) + list(after_tabs)))
        if not all_keys:
            continue

        result.lines.append(f"## {group}")

        for key in all_keys:
            if key in before_tabs and key not in after_tabs:
                tab = before_tabs[key]
                result.lines.append(f"- [{tab.title}]({tab.url})")
                result.removed_count += 1
            elif key in after_tabs and key not in before_tabs:
                tab = after_tabs[key]
                result.lines.append(f"+ [{tab.title}]({tab.url})")
                result.added_count += 1
            else:
                tab = after_tabs[key]
                result.lines.append(f"  [{tab.title}]({tab.url})")
                result.unchanged_count += 1

    return result
