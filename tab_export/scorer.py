"""Score tabs by relevance based on keyword weights."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from tab_export.parser import Tab, TabExport


@dataclass
class ScoredTab:
    tab: Tab
    score: float

    @property
    def title(self) -> str:
        return self.tab.title

    @property
    def url(self) -> str:
        return self.tab.url


@dataclass
class ScoringResult:
    scored: Dict[str, List[ScoredTab]]
    _source: TabExport

    @property
    def top_tabs(self) -> List[ScoredTab]:
        """Return all scored tabs sorted by score descending."""
        all_tabs = [
            st for tabs in self.scored.values() for st in tabs
        ]
        return sorted(all_tabs, key=lambda st: st.score, reverse=True)

    def as_export(self, min_score: float = 0.0) -> TabExport:
        """Return a TabExport containing only tabs at or above min_score."""
        groups: Dict[str, List[Tab]] = {}
        for group, tabs in self.scored.items():
            kept = [st.tab for st in tabs if st.score >= min_score]
            if kept:
                groups[group] = kept
        return TabExport(
            groups=groups,
            source_file=self._source.source_file,
        )


def _score_tab(tab: Tab, weights: Dict[str, float]) -> float:
    """Compute a relevance score for a single tab given keyword weights."""
    score = 0.0
    combined = f"{tab.title} {tab.url}".lower()
    for keyword, weight in weights.items():
        if keyword.lower() in combined:
            score += weight
    return score


def score_export(
    export: TabExport,
    weights: Dict[str, float],
) -> ScoringResult:
    """Score every tab in *export* using the provided keyword weights map.

    Args:
        export:  The parsed tab export to score.
        weights: Mapping of keyword -> numeric weight.  Weights may be
                 negative to penalise unwanted tabs.

    Returns:
        A :class:`ScoringResult` with per-group scored tab lists.
    """
    scored: Dict[str, List[ScoredTab]] = {}
    for group, tabs in export.groups.items():
        scored[group] = [
            ScoredTab(tab=tab, score=_score_tab(tab, weights))
            for tab in tabs
        ]
    return ScoringResult(scored=scored, _source=export)
