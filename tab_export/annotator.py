"""Annotator: attach user-defined notes to tabs by URL or title keyword."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from tab_export.parser import Tab, TabExport


@dataclass
class AnnotationRule:
    """A rule that matches tabs and attaches a note."""

    note: str
    url_contains: Optional[str] = None
    title_contains: Optional[str] = None

    def matches(self, tab: Tab) -> bool:
        url_ok = self.url_contains is None or self.url_contains.lower() in tab.url.lower()
        title_ok = self.title_contains is None or self.title_contains.lower() in tab.title.lower()
        return url_ok and title_ok


@dataclass
class AnnotationResult:
    export: TabExport
    annotations: Dict[str, str] = field(default_factory=dict)  # url -> note

    @property
    def total_annotated(self) -> int:
        return len(self.annotations)


def annotate_export(
    export: TabExport,
    rules: List[AnnotationRule],
) -> AnnotationResult:
    """Apply annotation rules to tabs; first matching rule wins per tab."""
    annotations: Dict[str, str] = {}

    for group_name, tabs in export.groups():
        for tab in tabs:
            for rule in rules:
                if rule.matches(tab):
                    annotations[tab.url] = rule.note
                    break

    return AnnotationResult(export=export, annotations=annotations)
