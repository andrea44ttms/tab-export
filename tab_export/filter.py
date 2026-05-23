"""Filtering utilities for tab exports."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from tab_export.parser import Tab, TabExport


@dataclass
class FilterOptions:
    """Options controlling how tabs are filtered."""

    keyword: Optional[str] = None          # substring match against title or URL
    url_pattern: Optional[str] = None      # regex applied to URL only
    group_name: Optional[str] = None       # exact group name match (case-insensitive)
    exclude_groups: list[str] = field(default_factory=list)  # groups to drop entirely


@dataclass
class FilterResult:
    """Outcome of a filter operation."""

    export: TabExport
    removed_count: int


def _tab_matches(tab: Tab, opts: FilterOptions) -> bool:
    """Return True if *tab* satisfies every active filter criterion."""
    if opts.keyword:
        kw = opts.keyword.lower()
        if kw not in tab.title.lower() and kw not in tab.url.lower():
            return False

    if opts.url_pattern:
        if not re.search(opts.url_pattern, tab.url):
            return False

    return True


def filter_export(export: TabExport, opts: FilterOptions) -> FilterResult:
    """Apply *opts* to *export* and return a :class:`FilterResult`.

    Groups are preserved even when all their tabs are removed so that
    callers can decide whether to strip empty groups themselves.
    """
    excluded = {g.lower() for g in opts.exclude_groups}
    removed = 0
    new_groups: dict[str, list[Tab]] = {}

    for group, tabs in export.groups.items():
        # Drop the entire group when it is explicitly excluded.
        if group.lower() in excluded:
            removed += len(tabs)
            continue

        # Skip groups that don't match the requested group name filter.
        if opts.group_name and group.lower() != opts.group_name.lower():
            removed += len(tabs)
            continue

        kept: list[Tab] = []
        for tab in tabs:
            if _tab_matches(tab, opts):
                kept.append(tab)
            else:
                removed += 1
        new_groups[group] = kept

    filtered_export = TabExport(
        source_file=export.source_file,
        raw_groups=new_groups,
    )
    return FilterResult(export=filtered_export, removed_count=removed)
