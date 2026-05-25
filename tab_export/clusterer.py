"""Cluster tabs into thematic groups using keyword-based heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from tab_export.parser import Tab, TabExport

# Ordered list of (cluster_name, keywords) — first match wins
_CLUSTER_RULES: List[tuple[str, List[str]]] = [
    ("Development", ["github", "gitlab", "stackoverflow", "docs.python", "developer", "api", "npm", "pypi"]),
    ("News", ["news", "bbc", "cnn", "reuters", "theguardian", "techcrunch", "ycombinator"]),
    ("Shopping", ["amazon", "ebay", "etsy", "shop", "store", "cart", "buy"]),
    ("Social", ["twitter", "x.com", "reddit", "linkedin", "facebook", "instagram", "mastodon"]),
    ("Video", ["youtube", "vimeo", "twitch", "netflix", "video", "watch"]),
    ("Docs / Reference", ["docs", "wiki", "manual", "reference", "cheatsheet", "guide", "howto"]),
    ("Tools", ["app", "tool", "dashboard", "console", "admin", "settings"]),
]

_UNCATEGORISED = "Uncategorised"


def _cluster_for_tab(tab: Tab) -> str:
    haystack = (tab.title + " " + tab.url).lower()
    for cluster_name, keywords in _CLUSTER_RULES:
        if any(kw in haystack for kw in keywords):
            return cluster_name
    return _UNCATEGORISED


@dataclass
class ClusteringResult:
    export: TabExport
    cluster_map: Dict[str, str] = field(default_factory=dict)  # url -> cluster

    @property
    def total_clustered(self) -> int:
        """Number of tabs assigned to a named (non-Uncategorised) cluster."""
        return sum(1 for c in self.cluster_map.values() if c != _UNCATEGORISED)

    @property
    def cluster_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for cluster in self.cluster_map.values():
            counts[cluster] = counts.get(cluster, 0) + 1
        return counts


def cluster_tabs(export: TabExport) -> ClusteringResult:
    """Assign each tab a thematic cluster label.

    Returns a :class:`ClusteringResult` whose ``export`` is a *new*
    ``TabExport`` where every tab's ``note`` field is prefixed with the
    cluster label (e.g. ``[Development]``) and ``cluster_map`` maps each
    URL to its cluster name.
    """
    cluster_map: Dict[str, str] = {}
    new_groups = {}

    for group_name, tabs in export.groups.items():
        new_tabs: List[Tab] = []
        for tab in tabs:
            cluster = _cluster_for_tab(tab)
            cluster_map[tab.url] = cluster
            existing_note = tab.note or ""
            prefix = f"[{cluster}] "
            new_note = prefix + existing_note if existing_note else prefix.rstrip()
            new_tabs.append(
                Tab(
                    title=tab.title,
                    url=tab.url,
                    group=tab.group,
                    note=new_note,
                    tags=tab.tags,
                )
            )
        new_groups[group_name] = new_tabs

    new_export = TabExport(
        raw_groups=new_groups,
        source_file=export.source_file,
    )
    return ClusteringResult(export=new_export, cluster_map=cluster_map)
