"""Tests for the deduplication module."""

from __future__ import annotations

import pytest

from tab_export.deduplicator import deduplicate, DeduplicationResult
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def export_with_dupes() -> TabExport:
    tabs = [
        Tab(group="Work", title="GitHub", url="https://github.com"),
        Tab(group="Work", title="GitHub Dup", url="https://github.com"),
        Tab(group="Work", title="Python", url="https://python.org"),
        Tab(group="Personal", title="GitHub Again", url="https://github.com"),
        Tab(group="Personal", title="News", url="https://news.ycombinator.com"),
        Tab(group="Personal", title="News Dup", url="https://news.ycombinator.com"),
    ]
    return TabExport(tabs=tabs)


def test_returns_deduplication_result(export_with_dupes):
    result = deduplicate(export_with_dupes)
    assert isinstance(result, DeduplicationResult)


def test_removed_count_across_groups(export_with_dupes):
    result = deduplicate(export_with_dupes, across_groups=True)
    # github.com appears 3 times (keep 1, remove 2)
    # news.yc appears 2 times (keep 1, remove 1)
    assert result.removed_count == 3


def test_removed_count_within_group_only(export_with_dupes):
    result = deduplicate(export_with_dupes, across_groups=False)
    # Within Work: github.com duplicated once -> remove 1
    # Within Personal: github.com is NOT a dup (different group); news.yc dup -> remove 1
    assert result.removed_count == 2


def test_clean_export_preserves_groups(export_with_dupes):
    result = deduplicate(export_with_dupes)
    assert set(result.export.groups) == {"Work", "Personal"}


def test_clean_export_has_fewer_tabs(export_with_dupes):
    result = deduplicate(export_with_dupes)
    assert len(result.export.tabs) < len(export_with_dupes.tabs)


def test_no_duplicates_unchanged():
    tabs = [
        Tab(group="A", title="One", url="https://one.com"),
        Tab(group="A", title="Two", url="https://two.com"),
    ]
    export = TabExport(tabs=tabs)
    result = deduplicate(export)
    assert result.removed_count == 0
    assert len(result.export.tabs) == 2


def test_source_file_preserved(export_with_dupes):
    export_with_dupes.source_file = "my_tabs.txt"
    result = deduplicate(export_with_dupes)
    assert result.export.source_file == "my_tabs.txt"


def test_removed_tabs_are_tab_instances(export_with_dupes):
    result = deduplicate(export_with_dupes)
    for tab in result.removed:
        assert isinstance(tab, Tab)
