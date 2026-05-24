"""Group tabs by domain or custom rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse

from tab_export.parser import Tab, TabExport


class GroupBy(str, Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"


@dataclass
class GroupingResult:
    export: TabExport
    original_group_count: int
    new_group_count: int

    @property
    def groups_added(self) -> int:
        return self.new_group_count - self.original_group_count


def _extract_key(url: str, by: GroupBy) -> str:
    """Return the grouping key for a URL."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or "unknown"
    except Exception:
        return "unknown"

    if by == GroupBy.SUBDOMAIN:
        return hostname

    # GroupBy.DOMAIN — strip leading 'www.'
    parts = hostname.lstrip(".").split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return hostname


def group_tabs_by(
    export: TabExport,
    by: GroupBy = GroupBy.DOMAIN,
    preserve_existing: bool = False,
) -> GroupingResult:
    """Re-group all tabs in *export* by domain (or subdomain).

    If *preserve_existing* is True, tabs that already belong to a named group
    keep that group name; only ungrouped tabs (group == "") are re-grouped.
    """
    original_group_count = len(export.groups())
    grouped: dict[str, list[Tab]] = {}

    for tab in export.tabs:
        if preserve_existing and tab.group:
            key = tab.group
        else:
            key = _extract_key(tab.url, by)

        grouped.setdefault(key, []).append(tab)

    new_tabs: list[Tab] = []
    for group_name in sorted(grouped):
        for tab in grouped[group_name]:
            new_tabs.append(
                Tab(
                    url=tab.url,
                    title=tab.title,
                    group=group_name,
                )
            )

    new_export = TabExport(tabs=new_tabs, source_file=export.source_file)
    return GroupingResult(
        export=new_export,
        original_group_count=original_group_count,
        new_group_count=len(new_export.groups()),
    )
