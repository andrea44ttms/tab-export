"""Assign freeform labels to tabs based on pattern rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from tab_export.parser import Tab, TabExport


@dataclass
class LabelRule:
    label: str
    keyword: Optional[str] = None
    url_contains: Optional[str] = None
    title_contains: Optional[str] = None

    def matches(self, tab: Tab) -> bool:
        if self.keyword:
            kw = self.keyword.lower()
            if kw in tab.title.lower() or kw in tab.url.lower():
                return True
        if self.url_contains and self.url_contains.lower() in tab.url.lower():
            return True
        if self.title_contains and self.title_contains.lower() in tab.title.lower():
            return True
        return False


@dataclass
class LabelingResult:
    export: TabExport
    label_map: dict = field(default_factory=dict)  # tab url -> list[str]

    @property
    def total_labeled(self) -> int:
        return sum(1 for labels in self.label_map.values() if labels)

    def labels_for(self, tab: Tab) -> List[str]:
        return self.label_map.get(tab.url, [])


def label_export(export: TabExport, rules: List[LabelRule]) -> LabelingResult:
    """Apply label rules to all tabs; a tab may receive multiple labels."""
    label_map: dict = {}

    for group_name, tabs in export.groups():
        for tab in tabs:
            matched: List[str] = []
            for rule in rules:
                if rule.matches(tab) and rule.label not in matched:
                    matched.append(rule.label)
            if matched:
                label_map[tab.url] = matched

    return LabelingResult(export=export, label_map=label_map)
