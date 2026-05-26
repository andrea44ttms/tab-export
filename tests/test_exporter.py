"""Tests for tab_export.exporter pipeline."""
from __future__ import annotations

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.exporter import PipelineOptions, PipelineResult, run_pipeline
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.filter import FilterOptions


@pytest.fixture()
def base_export() -> TabExport:
    return TabExport(
        source_file="test.txt",
        raw_groups={
            "Work": [
                Tab(title="GitHub", url="https://github.com"),
                Tab(title="Jira", url="https://jira.example.com"),
                Tab(title="GitHub", url="https://github.com"),  # duplicate
            ],
            "News": [
                Tab(title="BBC", url="https://bbc.co.uk"),
                Tab(title="Reuters", url="https://reuters.com"),
            ],
        },
    )


def test_run_pipeline_returns_pipeline_result(base_export: TabExport) -> None:
    result = run_pipeline(base_export)
    assert isinstance(result, PipelineResult)


def test_pipeline_output_is_nonempty(base_export: TabExport) -> None:
    result = run_pipeline(base_export)
    assert len(result.output) > 0


def test_pipeline_deduplication_removes_dupes(base_export: TabExport) -> None:
    opts = PipelineOptions(deduplicate=True)
    result = run_pipeline(base_export, opts)
    assert result.tabs_removed >= 1


def test_pipeline_no_dedup_leaves_zero(base_export: TabExport) -> None:
    opts = PipelineOptions(deduplicate=False)
    result = run_pipeline(base_export, opts)
    assert result.tabs_removed == 0


def test_tabs_before_counts_all_tabs(base_export: TabExport) -> None:
    opts = PipelineOptions(deduplicate=False)
    result = run_pipeline(base_export, opts)
    assert result.tabs_before == 5


def test_tabs_after_reflects_dedup(base_export: TabExport) -> None:
    opts = PipelineOptions(deduplicate=True)
    result = run_pipeline(base_export, opts)
    assert result.tabs_after == result.tabs_before - result.tabs_removed


def test_pipeline_notion_format(base_export: TabExport) -> None:
    opts = PipelineOptions(output_format="notion", deduplicate=False)
    result = run_pipeline(base_export, opts)
    assert "###" in result.output


def test_pipeline_with_filter_reduces_tabs(base_export: TabExport) -> None:
    filter_opts = FilterOptions(keywords=["github"])
    opts = PipelineOptions(deduplicate=False, filter=filter_opts)
    result = run_pipeline(base_export, opts)
    assert result.tabs_after < result.tabs_before


def test_pipeline_with_sort_does_not_change_count(base_export: TabExport) -> None:
    sort_opts = SortOptions(key=SortKey.TITLE, order=SortOrder.ASC)
    opts = PipelineOptions(deduplicate=False, sort=sort_opts)
    result = run_pipeline(base_export, opts)
    assert result.tabs_before == result.tabs_after


def test_default_options_applied_when_none_passed(base_export: TabExport) -> None:
    result = run_pipeline(base_export, None)
    assert isinstance(result, PipelineResult)
    assert result.tabs_removed >= 1
