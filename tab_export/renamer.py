"""Rename tab titles using find-and-replace or regex rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from tab_export.parser import Tab, TabExport


@dataclass
class RenameRule:
    pattern: str
    replacement: str
    use_regex: bool = False
    case_sensitive: bool = True

    def apply(self, text: str) -> str:
        if self.use_regex:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            return re.sub(self.pattern, self.replacement, text, flags=flags)
        if self.case_sensitive:
            return text.replace(self.pattern, self.replacement)
        pattern_re = re.compile(re.escape(self.pattern), re.IGNORECASE)
        return pattern_re.sub(self.replacement, text)


@dataclass
class RenamingResult:
    export: TabExport
    _total_renamed: int = field(default=0, repr=False)

    @property
    def total_renamed(self) -> int:
        return self._total_renamed


def _rename_tab(tab: Tab, rules: List[RenameRule]) -> tuple[Tab, bool]:
    new_title = tab.title
    for rule in rules:
        new_title = rule.apply(new_title)
    changed = new_title != tab.title
    if changed:
        return Tab(url=tab.url, title=new_title, group=tab.group), True
    return tab, False


def rename_export(export: TabExport, rules: List[RenameRule]) -> RenamingResult:
    """Apply rename rules to all tab titles in the export."""
    if not rules:
        return RenamingResult(export=export, _total_renamed=0)

    total_renamed = 0
    new_groups: dict[str, list[Tab]] = {}

    for group_name in export.groups:
        new_tabs = []
        for tab in export.tabs_in_group(group_name):
            renamed_tab, changed = _rename_tab(tab, rules)
            new_tabs.append(renamed_tab)
            if changed:
                total_renamed += 1
        new_groups[group_name] = new_tabs

    new_export = TabExport(
        source_file=export.source_file,
        _groups=new_groups,
    )
    return RenamingResult(export=new_export, _total_renamed=total_renamed)
