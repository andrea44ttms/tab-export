"""Tests for tab_export.exporter_v2."""
import pytest
from tab_export.parser import Tab, TabExport
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.filter import FilterOptions
from tab_export.exporter_v2 import SnapshotOptions, SnapshotResult, run_snapshot


@pytest.fixture
def base_export():
    return TabExport(
        groups={
            "Work": [
                Tab(title="GitHub", url="https://github.com"),
                Tab(title="GitHub", url="https://github.com"),  # duplicate
                Tab(title="Jira", url="https://jira.example.com"),
            ],
            "News": [
                Tab(title="BBC", url="https://bbc.co.uk"),
                Tab(title="Hacker News", url="https://news.ycombinator.com"),
            ],
        },
        source_file="test.txt",
    )


def test_run_snapshot_returns_snapshot_result(base_export):
    result = run_snapshot(base_export)
    assert isinstance(result, SnapshotResult)


def test_output_is_nonempty(base_export):
    result = run_snapshot(base_export)
    assert len(result.output) > 0


def test_tabs_before_counts_all_tabs(base_export):
    result = run_snapshot(base_export)
    assert result.tabs_before == 5


def test_dedup_removes_duplicate(base_export):
    result = run_snapshot(base_export, SnapshotOptions(deduplicate=True))
    assert result.removed_duplicates == 1
    assert result.tabs_after == 4


def test_no_dedup_leaves_all_tabs(base_export):
    result = run_snapshot(base_export, SnapshotOptions(deduplicate=False))
    assert result.removed_duplicates == 0
    assert result.tabs_after == 5


def test_filter_reduces_tabs(base_export):
    opts = SnapshotOptions(
        deduplicate=False,
        filter=FilterOptions(keyword="github"),
    )
    result = run_snapshot(base_export, opts)
    assert result.filtered_out > 0
    assert result.tabs_after < result.tabs_before


def test_tabs_removed_property(base_export):
    result = run_snapshot(base_export, SnapshotOptions(deduplicate=True))
    assert result.tabs_removed == result.tabs_before - result.tabs_after


def test_diff_is_none_without_previous(base_export):
    result = run_snapshot(base_export)
    assert result.diff is None
    assert result.has_diff is False


def test_diff_populated_with_previous(base_export):
    previous = TabExport(
        groups={"Work": [Tab(title="Old Tab", url="https://old.example.com")]},
        source_file="prev.txt",
    )
    opts = SnapshotOptions(previous=previous)
    result = run_snapshot(base_export, opts)
    assert result.diff is not None
    assert result.has_diff is True


def test_notion_format_output(base_export):
    opts = SnapshotOptions(output_format="notion")
    result = run_snapshot(base_export, opts)
    assert "###" in result.output


def test_sort_option_applied(base_export):
    opts = SnapshotOptions(
        deduplicate=False,
        sort=SortOptions(key=SortKey.TITLE, order=SortOrder.ASC),
    )
    result = run_snapshot(base_export, opts)
    assert result.output
    assert result.tabs_after == 5
