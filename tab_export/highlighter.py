"""Highlight matching keywords in tab titles and URLs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from tab_export.parser import Tab, TabExport


@dataclass
class HighlightOptions:
    keywords: List[str] = field(default_factory=list)
    marker_open: str = "**"
    marker_close: str = "**"


@dataclass
class HighlightResult:
    export: TabExport
    total_highlighted: int

    @property
    def was_highlighted(self) -> bool:
        return self.total_highlighted > 0


def _highlight_text(text: str, keywords: List[str], open_: str, close_: str) -> tuple[str, bool]:
    """Return (highlighted_text, was_changed)."""
    result = text
    changed = False
    for kw in keywords:
        lower_result = result.lower()
        lower_kw = kw.lower()
        idx = lower_result.find(lower_kw)
        if idx == -1:
            continue
        changed = True
        # Replace all occurrences (case-insensitive, preserving original case)
        parts = []
        pos = 0
        while True:
            idx = result.lower().find(lower_kw, pos)
            if idx == -1:
                parts.append(result[pos:])
                break
            parts.append(result[pos:idx])
            parts.append(f"{open_}{result[idx:idx + len(kw)]}{close_}")
            pos = idx + len(kw)
        result = "".join(parts)
    return result, changed


def _highlight_tab(tab: Tab, opts: HighlightOptions) -> tuple[Tab, bool]:
    if not opts.keywords:
        return tab, False
    new_title, t_changed = _highlight_text(
        tab.title, opts.keywords, opts.marker_open, opts.marker_close
    )
    new_url, u_changed = _highlight_text(
        tab.url, opts.keywords, opts.marker_open, opts.marker_close
    )
    changed = t_changed or u_changed
    if not changed:
        return tab, False
    return Tab(title=new_title, url=new_url, group=tab.group, tags=tab.tags), True


def highlight_export(export: TabExport, opts: HighlightOptions) -> HighlightResult:
    """Apply keyword highlighting to all tabs in the export."""
    if not opts.keywords:
        return HighlightResult(export=export, total_highlighted=0)

    total = 0
    new_data: dict[str, list[Tab]] = {}
    for group, tabs in export._data.items():
        new_tabs = []
        for tab in tabs:
            new_tab, changed = _highlight_tab(tab, opts)
            new_tabs.append(new_tab)
            if changed:
                total += 1
        new_data[group] = new_tabs

    new_export = TabExport(source_file=export.source_file, _data=new_data)
    return HighlightResult(export=new_export, total_highlighted=total)
