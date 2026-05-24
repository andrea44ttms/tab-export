"""Automatic tag inference for tabs based on URL and title patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from tab_export.parser import Tab, TabExport

# Simple keyword-to-tag mapping applied to title and URL
_RULES: Dict[str, List[str]] = {
    "github.com": ["dev", "code"],
    "stackoverflow.com": ["dev", "qa"],
    "docs.": ["docs"],
    "wikipedia.org": ["reference"],
    "youtube.com": ["video"],
    "reddit.com": ["social"],
    "twitter.com": ["social"],
    "x.com": ["social"],
    "news": ["news"],
    "blog": ["blog"],
    "tutorial": ["learning"],
    "learn": ["learning"],
    "course": ["learning"],
    "arxiv.org": ["research", "paper"],
    "paper": ["research"],
}


@dataclass
class TaggingResult:
    export: TabExport
    tag_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def total_tagged(self) -> int:
        return sum(self.tag_counts.values())


def _infer_tags(tab: Tab) -> List[str]:
    """Return a deduplicated list of inferred tags for a single tab."""
    combined = (tab.url + " " + tab.title).lower()
    tags: List[str] = []
    for pattern, assigned in _RULES.items():
        if pattern in combined:
            tags.extend(assigned)
    # preserve order, deduplicate
    seen = set()
    unique: List[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def tag_export(export: TabExport) -> TaggingResult:
    """Annotate each tab's title with inferred tags and return a TaggingResult."""
    tag_counts: Dict[str, int] = {}
    new_groups = {}
    for group, tabs in export._groups.items():
        new_tabs = []
        for tab in tabs:
            tags = _infer_tags(tab)
            if tags:
                tag_str = " ".join(f"[{t}]" for t in tags)
                new_title = f"{tab.title} {tag_str}"
                new_tabs.append(Tab(url=tab.url, title=new_title, group=tab.group))
                for t in tags:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
            else:
                new_tabs.append(tab)
        new_groups[group] = new_tabs
    new_export = TabExport(source_file=export.source_file)
    new_export._groups = new_groups
    return TaggingResult(export=new_export, tag_counts=tag_counts)
