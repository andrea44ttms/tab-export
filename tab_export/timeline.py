"""Timeline module: groups tabs by inferred recency/time category."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from tab_export.parser import Tab, TabExport

# Heuristic keyword buckets mapped to timeline labels
_TIMELINE_PATTERNS: List[Tuple[str, List[str]]] = [
    ("today", ["today", "now", "live", "breaking", "latest"]),
    ("this-week", ["week", "weekly", "digest", "recap"]),
    ("this-month", ["month", "monthly", "release", "changelog"]),
    ("older", ["archive", "history", "legacy", "old", "2020", "2021", "2022"]),
]
_DEFAULT_LABEL = "uncategorized"


def _infer_timeline_label(tab: Tab) -> str:
    combined = (tab.title + " " + tab.url).lower()
    for label, keywords in _TIMELINE_PATTERNS:
        if any(kw in combined for kw in keywords):
            return label
    return _DEFAULT_LABEL


@dataclass
class TimelineResult:
    """Result of grouping tabs into timeline buckets."""
    buckets: Dict[str, List[Tab]] = field(default_factory=dict)

    @property
    def total_bucketed(self) -> int:
        return sum(len(tabs) for label, tabs in self.buckets.items() if label != _DEFAULT_LABEL)

    @property
    def bucket_names(self) -> List[str]:
        return list(self.buckets.keys())

    def summary_lines(self) -> List[str]:
        lines = ["Timeline summary:"]
        for label, tabs in self.buckets.items():
            lines.append(f"  {label}: {len(tabs)} tab(s)")
        return lines


def build_timeline(export: TabExport) -> TimelineResult:
    """Assign each tab in the export to a timeline bucket."""
    buckets: Dict[str, List[Tab]] = {}

    for group in export.groups():
        for tab in export.tabs_in_group(group):
            label = _infer_timeline_label(tab)
            buckets.setdefault(label, []).append(tab)

    # Ensure canonical order
    ordered: Dict[str, List[Tab]] = {}
    for label, _ in _TIMELINE_PATTERNS:
        if label in buckets:
            ordered[label] = buckets[label]
    if _DEFAULT_LABEL in buckets:
        ordered[_DEFAULT_LABEL] = buckets[_DEFAULT_LABEL]

    return TimelineResult(buckets=ordered)
