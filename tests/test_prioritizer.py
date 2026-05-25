"""Tests for tab_export.prioritizer."""
from __future__ import annotations

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.prioritizer import (
    PriorityRule,
    PrioritizingResult,
    prioritize_export,
)


@pytest.fixture()
def sample_export() -> TabExport:
    tabs = [
        Tab(title="GitHub Repo", url="https://github.com/user/repo", group="Dev"),
        Tab(title="BBC News", url="https://bbc.co.uk/news", group="News"),
        Tab(title="Python Docs", url="https://docs.python.org", group="Dev"),
        Tab(title="Random Blog", url="https://example.com/blog", group="Other"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


@pytest.fixture()
def rules() -> list:
    return [
        PriorityRule(keyword="github", field="url", priority=10),
        PriorityRule(keyword="docs", field="title", priority=8),
        PriorityRule(keyword="news", field="title", priority=5),
    ]


def test_prioritize_returns_prioritizing_result(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    assert isinstance(result, PrioritizingResult)


def test_priority_map_covers_all_tabs(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    all_tabs = [
        tab
        for g in sample_export.groups
        for tab in sample_export.tabs_in_group(g)
    ]
    assert set(result.priority_map.keys()) == set(all_tabs)


def test_github_tab_gets_priority_10(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    github_tab = next(
        t for t in result.priority_map if "github" in t.url.lower()
    )
    assert result.priority_for(github_tab) == 10


def test_docs_tab_gets_priority_8(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    docs_tab = next(t for t in result.priority_map if "Docs" in t.title)
    assert result.priority_for(docs_tab) == 8


def test_unmatched_tab_gets_priority_0(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    random_tab = next(t for t in result.priority_map if "Random" in t.title)
    assert result.priority_for(random_tab) == 0


def test_total_prioritized_counts_nonzero(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    assert result.total_prioritized == 3


def test_no_rules_all_priority_zero(sample_export):
    result = prioritize_export(sample_export, rules=[])
    assert result.total_prioritized == 0


def test_top_tabs_ordered_by_priority_desc(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    top = result.top_tabs(n=3)
    priorities = [result.priority_for(t) for t in top]
    assert priorities == sorted(priorities, reverse=True)


def test_top_tabs_respects_n_limit(sample_export, rules):
    result = prioritize_export(sample_export, rules)
    assert len(result.top_tabs(n=2)) <= 2


def test_higher_priority_rule_wins_on_multiple_matches():
    tab = Tab(title="GitHub Docs", url="https://github.com/docs", group="Dev")
    export = TabExport(tabs=[tab], source_file="t.txt")
    rules = [
        PriorityRule(keyword="github", field="url", priority=10),
        PriorityRule(keyword="docs", field="title", priority=8),
    ]
    result = prioritize_export(export, rules)
    assert result.priority_for(tab) == 10
