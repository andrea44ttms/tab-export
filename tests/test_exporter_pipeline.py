"""Tests for the full pipeline runner in exporter_pipeline.py."""

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.filter import FilterOptions
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.truncator import TruncateOptions
from tab_export.exporter_pipeline import (
    FullPipelineOptions,
    FullPipelineResult,
    run_full_pipeline,
)


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        source_file="test.txt",
        groups=[
            "Work",
            "Personal",
        ],
        tabs_in_group={
            "Work": [
                Tab(title="GitHub", url="https://github.com"),
                Tab(title="GitHub", url="https://github.com"),  # duplicate
                Tab(title="Jira", url="https://jira.example.com"),
            ],
            "Personal": [
                Tab(title="Reddit", url="https://reddit.com"),
                Tab(title="News Site", url="https://news.example.com"),
            ],
        },
    )


def test_run_full_pipeline_returns_result_type(sample_export):
    result = run_full_pipeline(sample_export)
    assert isinstance(result, FullPipelineResult)


def test_output_is_nonempty_string(sample_export):
    result = run_full_pipeline(sample_export)
    assert isinstance(result.output, str)
    assert len(result.output) > 0


def test_default_options_deduplicates(sample_export):
    result = run_full_pipeline(sample_export)
    assert result.removed_duplicates == 1


def test_tabs_before_counts_all_tabs(sample_export):
    result = run_full_pipeline(sample_export)
    assert result.tabs_before == 5


def test_tabs_after_reflects_dedup(sample_export):
    result = run_full_pipeline(sample_export)
    assert result.tabs_after == 4


def test_no_dedup_option_leaves_duplicates(sample_export):
    opts = FullPipelineOptions(deduplicate=False)
    result = run_full_pipeline(sample_export, opts)
    assert result.removed_duplicates == 0
    assert result.tabs_after == 5


def test_filter_step_is_recorded(sample_export):
    opts = FullPipelineOptions(
        filter_opts=FilterOptions(keywords=["GitHub"]),
        deduplicate=False,
    )
    result = run_full_pipeline(sample_export, opts)
    assert "filter" in result.steps_applied


def test_sort_step_is_recorded(sample_export):
    opts = FullPipelineOptions(
        sort_opts=SortOptions(key=SortKey.TITLE, order=SortOrder.ASC),
        deduplicate=False,
    )
    result = run_full_pipeline(sample_export, opts)
    assert "sort" in result.steps_applied


def test_deduplicate_step_is_recorded(sample_export):
    result = run_full_pipeline(sample_export)
    assert "deduplicate" in result.steps_applied


def test_truncate_step_is_recorded(sample_export):
    opts = FullPipelineOptions(
        truncate_opts=TruncateOptions(max_title_length=5),
    )
    result = run_full_pipeline(sample_export, opts)
    assert "truncate" in result.steps_applied


def test_notion_format_output(sample_export):
    opts = FullPipelineOptions(output_format="notion", deduplicate=False)
    result = run_full_pipeline(sample_export, opts)
    assert "###" in result.output


def test_no_steps_with_minimal_options(sample_export):
    opts = FullPipelineOptions(deduplicate=False)
    result = run_full_pipeline(sample_export, opts)
    assert result.steps_applied == []
