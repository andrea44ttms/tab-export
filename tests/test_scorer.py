"""Tests for tab_export.scorer."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.scorer import (
    ScoredTab,
    ScoringResult,
    score_export,
)


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        groups={
            "Dev": [
                Tab(title="GitHub Repo", url="https://github.com/user/repo"),
                Tab(title="Python Docs", url="https://docs.python.org"),
            ],
            "News": [
                Tab(title="Hacker News", url="https://news.ycombinator.com"),
                Tab(title="GitHub Blog", url="https://github.blog"),
            ],
        },
        source_file="test.txt",
    )


def test_score_export_returns_scoring_result(sample_export):
    result = score_export(sample_export, weights={"github": 1.0})
    assert isinstance(result, ScoringResult)


def test_scored_tabs_are_scored_tab_instances(sample_export):
    result = score_export(sample_export, weights={"github": 1.0})
    for tabs in result.scored.values():
        for st in tabs:
            assert isinstance(st, ScoredTab)


def test_matching_keyword_increases_score(sample_export):
    result = score_export(sample_export, weights={"github": 2.0})
    github_tab = result.scored["Dev"][0]  # GitHub Repo
    python_tab = result.scored["Dev"][1]  # Python Docs
    assert github_tab.score > python_tab.score


def test_negative_weight_penalises_tab(sample_export):
    result = score_export(sample_export, weights={"hacker": -3.0})
    hn_tab = next(
        st for st in result.scored["News"] if "Hacker" in st.title
    )
    assert hn_tab.score < 0


def test_no_weights_gives_zero_scores(sample_export):
    result = score_export(sample_export, weights={})
    for tabs in result.scored.values():
        for st in tabs:
            assert st.score == 0.0


def test_top_tabs_sorted_descending(sample_export):
    result = score_export(sample_export, weights={"github": 1.0, "docs": 0.5})
    scores = [st.score for st in result.top_tabs]
    assert scores == sorted(scores, reverse=True)


def test_top_tabs_contains_all_tabs(sample_export):
    result = score_export(sample_export, weights={})
    total = sum(len(tabs) for tabs in sample_export.groups.values())
    assert len(result.top_tabs) == total


def test_as_export_filters_by_min_score(sample_export):
    result = score_export(sample_export, weights={"github": 1.0})
    filtered = result.as_export(min_score=1.0)
    all_tabs = [
        tab for tabs in filtered.groups.values() for tab in tabs
    ]
    assert all("github" in tab.url.lower() or "github" in tab.title.lower() for tab in all_tabs)


def test_as_export_preserves_source_file(sample_export):
    result = score_export(sample_export, weights={})
    export = result.as_export()
    assert export.source_file == sample_export.source_file


def test_as_export_drops_empty_groups(sample_export):
    # weight only matches nothing → all scores 0, min_score=1 → no groups
    result = score_export(sample_export, weights={})
    export = result.as_export(min_score=1.0)
    assert len(export.groups) == 0
