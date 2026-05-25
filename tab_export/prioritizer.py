"""Prioritize tabs by assigning a numeric priority level based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tab_export.parser import Tab, TabExport


@dataclass
class PriorityRule:
    """A rule that assigns a priority level when a tab matches."""
    keyword: str
    field: str  # 'title' or 'url'
    priority: int  # higher = more important

    def matches(self, tab: Tab) -> bool:
        haystack = tab.title if self.field == "title" else tab.url
        return self.keyword.lower() in haystack.lower()


@dataclass
class PrioritizingResult:
    """Result of a prioritization pass."""
    export: TabExport
    priority_map: Dict[Tab, int] = field(default_factory=dict)

    @property
    def total_prioritized(self) -> int:
        return sum(1 for v in self.priority_map.values() if v > 0)

    def priority_for(self, tab: Tab) -> int:
        return self.priority_map.get(tab, 0)

    def top_tabs(self, n: int = 10) -> List[Tab]:
        """Return the top-n tabs by priority (descending)."""
        scored = [(tab, pri) for tab, pri in self.priority_map.items() if pri > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [tab for tab, _ in scored[:n]]


def _best_priority(tab: Tab, rules: List[PriorityRule]) -> int:
    best = 0
    for rule in rules:
        if rule.matches(tab):
            best = max(best, rule.priority)
    return best


def prioritize_export(
    export: TabExport,
    rules: List[PriorityRule],
) -> PrioritizingResult:
    """Assign priority levels to every tab in *export* using *rules*."""
    priority_map: Dict[Tab, int] = {}
    for group_name in export.groups:
        for tab in export.tabs_in_group(group_name):
            priority_map[tab] = _best_priority(tab, rules)
    return PrioritizingResult(export=export, priority_map=priority_map)
