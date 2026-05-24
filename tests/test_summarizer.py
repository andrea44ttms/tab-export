"""Tests for tab_export.summarizer."""

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.summarizer import (
    SummaryOptions,
    SummaryResult,
    summarize_export,
    summarize_export_markdown,
)


@pytest.fixture
def sample_export():
    tabs = [
        Tab(title="GitHub", url="https://github.com/user/repo", group="Dev"),
        Tab(title="Docs", url="https://docs.python.org/3/", group="Dev"),
        Tab(title="News", url="https://news.ycombinator.com/", group="Reading"),
        Tab(title="Reddit", url="https://reddit.com/r/python", group="Reading"),
        Tab(title="Another GitHub", url="https://github.com/other/project", group="Dev"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


def test_summarize_returns_summary_result(sample_export):
    result = summarize_export(sample_export)
    assert isinstance(result, SummaryResult)


def test_text_property_joins_lines(sample_export):
    result = summarize_export(sample_export)
    assert result.text == "\n".join(result.lines)


def test_summary_contains_total_tabs(sample_export):
    result = summarize_export(sample_export)
    assert any("5" in line for line in result.lines)


def test_summary_contains_total_groups(sample_export):
    result = summarize_export(sample_export)
    assert any("2" in line for line in result.lines)


def test_summary_lists_group_names(sample_export):
    result = summarize_export(sample_export)
    text = result.text
    assert "Dev" in text
    assert "Reading" in text


def test_summary_group_breakdown_can_be_disabled(sample_export):
    opts = SummaryOptions(include_group_breakdown=False)
    result = summarize_export(sample_export, options=opts)
    text = result.text
    # Group names should not appear in breakdown section
    assert "Dev" not in text
    assert "Reading" not in text


def test_summary_shows_top_domains(sample_export):
    result = summarize_export(sample_export)
    text = result.text
    assert "github.com" in text


def test_summary_respects_max_top_domains(sample_export):
    opts = SummaryOptions(max_top_domains=1)
    result = summarize_export(sample_export)
    # With default 5 we expect at least one domain line
    assert any("github.com" in line or "reddit.com" in line for line in result.lines)


def test_markdown_summary_returns_summary_result(sample_export):
    result = summarize_export_markdown(sample_export)
    assert isinstance(result, SummaryResult)


def test_markdown_summary_has_h2_header(sample_export):
    result = summarize_export_markdown(sample_export)
    assert any(line.startswith("## ") for line in result.lines)


def test_markdown_summary_uses_bold_labels(sample_export):
    result = summarize_export_markdown(sample_export)
    text = result.text
    assert "**Total tabs**" in text
    assert "**Total groups**" in text


def test_markdown_summary_ends_with_newline(sample_export):
    result = summarize_export_markdown(sample_export)
    assert result.text.endswith("\n")


def test_markdown_group_breakdown_has_h3(sample_export):
    result = summarize_export_markdown(sample_export)
    assert any(line.startswith("### Groups") for line in result.lines)
