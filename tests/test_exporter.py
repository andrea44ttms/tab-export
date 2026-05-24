"""Tests for the export pipeline in tab_export/exporter.py."""

import pytest
from tab_export.parser import TabExport, Tab
from tab_export.filter import FilterOptions
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.exporter import PipelineOptions, PipelineResult, run_pipeline


@pytest.fixture
def base_export():
    return TabExport(
        source_file="test.txt",
        raw_groups={
            "Work": [
                Tab(title="GitHub", url="https://github.com/org/repo"),
                Tab(title="GitHub", url="https://github.com/org/repo"),
                Tab(title="Jira", url="https://jira.example.com/board"),
            ],
            "News": [
                Tab(title="Hacker News", url="https://news.ycombinator.com"),
                Tab(title="Lobsters", url="https://lobste.rs"),
            ],
        },
    )


def test_run_pipeline_returns_pipeline_result(base_export):
    opts = PipelineOptions()
    result = run_pipeline(base_export, opts)
    assert isinstance(result, PipelineResult)


def test_pipeline_output_is_nonempty(base_export):
    opts = PipelineOptions()
    result = run_pipeline(base_export, opts)
    assert len(result.output) > 0


def test_pipeline_deduplication_removes_dupes(base_export):
    opts = PipelineOptions(deduplicate=True)
    result = run_pipeline(base_export, opts)
    assert result.removed_duplicates == 1


def test_pipeline_no_dedup_leaves_zero(base_export):
    opts = PipelineOptions(deduplicate=False)
    result = run_pipeline(base_export, opts)
    assert result.removed_duplicates == 0


def test_pipeline_filter_reduces_tabs(base_export):
    opts = PipelineOptions(filter_opts=FilterOptions(keyword="github"))
    result = run_pipeline(base_export, opts)
    assert result.filtered_out > 0
    assert "GitHub" in result.output
    assert "Jira" not in result.output


def test_pipeline_no_filter_keeps_all(base_export):
    opts = PipelineOptions()
    result = run_pipeline(base_export, opts)
    assert result.filtered_out == 0
    assert "Jira" in result.output


def test_pipeline_notion_format(base_export):
    opts = PipelineOptions(output_format="notion")
    result = run_pipeline(base_export, opts)
    assert "### " in result.output
    assert "## " not in result.output


def test_pipeline_stats_report_included(base_export):
    opts = PipelineOptions(include_stats=True)
    result = run_pipeline(base_export, opts)
    assert result.stats_report is not None
    assert len(result.stats_report) > 0


def test_pipeline_stats_report_excluded_by_default(base_export):
    opts = PipelineOptions()
    result = run_pipeline(base_export, opts)
    assert result.stats_report is None


def test_pipeline_sort_orders_tabs(base_export):
    opts = PipelineOptions(
        sort_opts=SortOptions(key=SortKey.TITLE, order=SortOrder.ASC)
    )
    result = run_pipeline(base_export, opts)
    assert isinstance(result.output, str)
    github_pos = result.output.find("GitHub")
    jira_pos = result.output.find("Jira")
    assert github_pos < jira_pos, "GitHub should appear before Jira when sorted ascending by title"


def test_pipeline_sort_descending_orders_tabs(base_export):
    """Jira should appear before GitHub when sorted descending by title."""
    opts = PipelineOptions(
        sort_opts=SortOptions(key=SortKey.TITLE, order=SortOrder.DESC)
    )
    result = run_pipeline(base_export, opts)
    github_pos = result.output.find("GitHub")
    jira_pos = result.output.find("Jira")
    assert jira_pos < github_pos, "Jira should appear before GitHub when sorted descending by title"
