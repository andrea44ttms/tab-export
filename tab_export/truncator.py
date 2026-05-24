"""Truncate tab titles and URLs to configurable max lengths."""

from dataclasses import dataclass
from typing import Optional

from tab_export.parser import Tab, TabExport


@dataclass
class TruncateOptions:
    max_title_length: Optional[int] = None
    max_url_length: Optional[int] = None
    ellipsis: str = "…"


@dataclass
class TruncationResult:
    export: TabExport
    tabs_truncated: int

    @property
    def was_truncated(self) -> bool:
        return self.tabs_truncated > 0


def _truncate_str(value: str, max_length: Optional[int], ellipsis: str) -> tuple[str, bool]:
    """Return (truncated_value, was_changed)."""
    if max_length is None or len(value) <= max_length:
        return value, False
    cut = max(0, max_length - len(ellipsis))
    return value[:cut] + ellipsis, True


def _truncate_tab(tab: Tab, options: TruncateOptions) -> tuple[Tab, bool]:
    new_title, title_changed = _truncate_str(
        tab.title, options.max_title_length, options.ellipsis
    )
    new_url, url_changed = _truncate_str(
        tab.url, options.max_url_length, options.ellipsis
    )
    changed = title_changed or url_changed
    if not changed:
        return tab, False
    return Tab(title=new_title, url=new_url, group=tab.group), True


def truncate_export(export: TabExport, options: TruncateOptions) -> TruncationResult:
    """Apply title/URL truncation to all tabs in the export."""
    truncated_count = 0
    new_tabs: list[Tab] = []

    for tab in export.tabs:
        new_tab, changed = _truncate_tab(tab, options)
        new_tabs.append(new_tab)
        if changed:
            truncated_count += 1

    new_export = TabExport(tabs=new_tabs, source_file=export.source_file)
    return TruncationResult(export=new_export, tabs_truncated=truncated_count)
