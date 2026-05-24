"""Tests for tab_export.merger."""

import pytest

from tab_export.merger import MergeResult, merge_exports
from tab_export.parser import Tab, TabExport


def _make_export(groups_tabs: dict, source: str = "") -> TabExport:
    tabs = [
        Tab(title=f"Tab {url}", url=url, group=group)
        for group, urls in groups_tabs.items()
        for url in urls
    ]
    return TabExport(tabs=tabs, source_file=source)


@pytest.fixture()
def base_export():
    return _make_export(
        {
            "Work": ["https://jira.example.com", "https://confluence.example.com"],
            "News": ["https://hn.example.com"],
        },
        source="base.txt",
    )


@pytest.fixture()
def incoming_export():
    return _make_export(
        {
            "Work": ["https://github.example.com", "https://jira.example.com"],
            "Personal": ["https://reddit.example.com"],
        },
        source="incoming.txt",
    )


def test_merge_returns_merge_result(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert isinstance(result, MergeResult)


def test_merge_result_has_correct_export_type(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert isinstance(result.export, TabExport)


def test_dedup_skips_existing_url(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export, deduplicate=True)
    work_urls = [t.url for t in result.export.tabs_in_group("Work")]
    assert work_urls.count("https://jira.example.com") == 1


def test_no_dedup_allows_duplicate_url(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export, deduplicate=False)
    work_urls = [t.url for t in result.export.tabs_in_group("Work")]
    assert work_urls.count("https://jira.example.com") == 2


def test_new_group_from_incoming_is_present(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert "Personal" in result.export.groups


def test_base_groups_preserved(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert "News" in result.export.groups


def test_tabs_added_count_with_dedup(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export, deduplicate=True)
    # github.example.com (new) + reddit.example.com (new) = 2
    assert result.tabs_added == 2


def test_tabs_added_count_without_dedup(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export, deduplicate=False)
    # All 3 incoming tabs added regardless
    assert result.tabs_added == 3


def test_source_files_recorded(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert "base.txt" in result.source_files
    assert "incoming.txt" in result.source_files


def test_summary_is_nonempty_string(base_export, incoming_export):
    result = merge_exports(base_export, incoming_export)
    assert isinstance(result.summary, str)
    assert len(result.summary) > 0


def test_merge_empty_incoming_leaves_base_intact(base_export):
    empty = TabExport(tabs=[], source_file="empty.txt")
    result = merge_exports(base_export, empty)
    assert set(result.export.groups) == set(base_export.groups)
    assert result.tabs_added == 0
