"""Bookmark detection and classification for tab exports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from tab_export.parser import Tab, TabExport


BOOKMARK_PATTERNS: Dict[str, List[str]] = {
    "docs": ["docs.", "/docs/", "documentation", "readthedocs", "devdocs"],
    "video": ["youtube.com", "vimeo.com", "twitch.tv", "/watch?"],
    "social": ["twitter.com", "x.com", "reddit.com", "linkedin.com", "mastodon"],
    "code": ["github.com", "gitlab.com", "bitbucket.org", "stackoverflow.com"],
    "news": ["news.", "/news/", "hn.algolia", "hackernews", "lobste.rs"],
    "shopping": ["amazon.", "ebay.", "shop.", "/product/", "/cart"],
}


@dataclass
class BookmarkClassification:
    tab: Tab
    category: str


@dataclass
class BookmarkResult:
    export: TabExport
    classifications: List[BookmarkClassification] = field(default_factory=list)

    @property
    def total_classified(self) -> int:
        return len(self.classifications)

    def by_category(self) -> Dict[str, List[Tab]]:
        result: Dict[str, List[Tab]] = {}
        for bc in self.classifications:
            result.setdefault(bc.category, []).append(bc.tab)
        return result


def _classify_tab(tab: Tab) -> str:
    combined = (tab.url + " " + tab.title).lower()
    for category, patterns in BOOKMARK_PATTERNS.items():
        if any(p in combined for p in patterns):
            return category
    return "other"


def classify_bookmarks(export: TabExport) -> BookmarkResult:
    """Classify each tab in the export into a bookmark category."""
    classifications: List[BookmarkClassification] = []
    for group in export.groups:
        for tab in export.tabs_in_group(group):
            category = _classify_tab(tab)
            if category != "other":
                classifications.append(BookmarkClassification(tab=tab, category=category))
    return BookmarkResult(export=export, classifications=classifications)
