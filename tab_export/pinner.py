"""Pin tabs by keyword or domain, marking them for priority treatment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from tab_export.parser import Tab, TabExport


@dataclass
class PinRule:
    """A rule that pins tabs whose title or URL contains a keyword."""
    keyword: str
    match_field: str = "both"  # "title", "url", or "both"

    def matches(self, tab: Tab) -> bool:
        kw = self.keyword.lower()
        if self.match_field in ("title", "both"):
            if kw in tab.title.lower():
                return True
        if self.match_field in ("url", "both"):
            if kw in tab.url.lower():
                return True
        return False


@dataclass
class PinningResult:
    """Result of a pinning operation."""
    export: TabExport
    pinned_urls: List[str] = field(default_factory=list)

    @property
    def total_pinned(self) -> int:
        return len(self.pinned_urls)


def pin_export(
    export: TabExport,
    rules: List[PinRule],
    pin_marker: str = "📌",
) -> PinningResult:
    """Apply pin rules to all tabs, prepending *pin_marker* to matching titles.

    Tabs that already start with the marker are not double-marked.
    Returns a :class:`PinningResult` containing the modified export and the
    URLs of every tab that was pinned.
    """
    if not rules:
        return PinningResult(export=export, pinned_urls=[])

    pinned_urls: List[str] = []
    new_groups: dict = {}

    for group_name, tabs in export.groups().items():
        updated_tabs: List[Tab] = []
        for tab in tabs:
            matched = any(rule.matches(tab) for rule in rules)
            if matched and not tab.title.startswith(pin_marker):
                tab = Tab(
                    title=f"{pin_marker} {tab.title}",
                    url=tab.url,
                    group=tab.group,
                )
                pinned_urls.append(tab.url)
            updated_tabs.append(tab)
        new_groups[group_name] = updated_tabs

    all_tabs: List[Tab] = []
    for tabs in new_groups.values():
        all_tabs.extend(tabs)

    new_export = TabExport(tabs=all_tabs, source_file=export.source_file)
    return PinningResult(export=new_export, pinned_urls=pinned_urls)
