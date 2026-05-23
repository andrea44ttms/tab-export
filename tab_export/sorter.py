"""Sorting utilities for tab exports."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from tab_export.parser import Tab, TabExport


class SortKey(str, Enum):
    TITLE = "title"
    URL = "url"
    GROUP = "group"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class SortOptions:
    key: SortKey = SortKey.TITLE
    order: SortOrder = SortOrder.ASC
    sort_groups: bool = False


def _tab_sort_key(tab: Tab, key: SortKey) -> str:
    if key == SortKey.TITLE:
        return (tab.title or "").lower()
    if key == SortKey.URL:
        return tab.url.lower()
    # GROUP key is handled at the group level
    return (tab.title or "").lower()


def sort_export(export: TabExport, options: SortOptions | None = None) -> TabExport:
    """Return a new TabExport with tabs (and optionally groups) sorted."""
    if options is None:
        options = SortOptions()

    reverse = options.order == SortOrder.DESC

    # Build sorted groups dict
    group_names = list(export._groups.keys())
    if options.sort_groups or options.key == SortKey.GROUP:
        group_names = sorted(group_names, key=str.lower, reverse=reverse)

    sorted_groups: dict[str, list[Tab]] = {}
    for group in group_names:
        tabs = list(export._groups[group])
        if options.key != SortKey.GROUP:
            tabs = sorted(
                tabs,
                key=lambda t: _tab_sort_key(t, options.key),
                reverse=reverse,
            )
        sorted_groups[group] = tabs

    new_export = TabExport.__new__(TabExport)
    new_export._groups = sorted_groups
    new_export.source_file = export.source_file
    return new_export
