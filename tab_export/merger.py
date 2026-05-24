"""Merge two TabExport objects into one, combining or deduplicating groups."""

from dataclasses import dataclass, field
from typing import Dict, List

from tab_export.parser import Tab, TabExport


@dataclass
class MergeResult:
    export: TabExport
    groups_merged: int
    tabs_added: int
    source_files: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"Merged {self.tabs_added} tab(s) across "
            f"{self.groups_merged} group(s) from "
            f"{len(self.source_files)} source(s)."
        )


def merge_exports(
    base: TabExport,
    incoming: TabExport,
    *,
    deduplicate: bool = True,
) -> MergeResult:
    """Merge *incoming* into *base*, returning a new TabExport.

    Parameters
    ----------
    base:
        The primary export that acts as the merge target.
    incoming:
        The export whose tabs are merged into *base*.
    deduplicate:
        When True, tabs whose URL already exists in the target group are
        skipped.  When False, all tabs from *incoming* are appended.
    """
    # Build a mutable copy of base groups: {group_name: [Tab, ...]}
    merged: Dict[str, List[Tab]] = {}
    for group in base.groups:
        merged[group] = list(base.tabs_in_group(group))

    groups_merged = 0
    tabs_added = 0

    for group in incoming.groups:
        incoming_tabs = list(incoming.tabs_in_group(group))
        if not incoming_tabs:
            continue

        if group not in merged:
            merged[group] = []
            groups_merged += 1
        else:
            groups_merged += 1

        existing_urls = {t.url for t in merged[group]} if deduplicate else set()

        for tab in incoming_tabs:
            if deduplicate and tab.url in existing_urls:
                continue
            merged[group].append(tab)
            existing_urls.add(tab.url)
            tabs_added += 1

    # Rebuild a flat list preserving order: base groups first, then new ones.
    all_tabs: List[Tab] = []
    for group_name, tabs in merged.items():
        for tab in tabs:
            # Ensure the group field matches the canonical key.
            all_tabs.append(Tab(title=tab.title, url=tab.url, group=group_name))

    new_export = TabExport(
        tabs=all_tabs,
        source_file=base.source_file,
    )

    sources = []
    if base.source_file:
        sources.append(base.source_file)
    if incoming.source_file and incoming.source_file not in sources:
        sources.append(incoming.source_file)

    return MergeResult(
        export=new_export,
        groups_merged=groups_merged,
        tabs_added=tabs_added,
        source_files=sources,
    )
