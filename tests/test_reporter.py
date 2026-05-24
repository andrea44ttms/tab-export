"""Tests for tab_export.reporter module."""
import pytest
from tab_export.stats import ExportStats
from tab_export.reporter import render_stats_text, render_stats_markdown


@pytest.fixture
def sample_stats():
    return ExportStats(
        total_tabs=7,
        total_groups=2,
        tabs_per_group={"Dev": 5, "Reading": 2},
        top_domains=[("github.com", 3), ("docs.python.org", 2)],
        empty_groups=[],
    )


@pytest.fixture
def stats_with_empty_group():
    return ExportStats(
        total_tabs=3,
        total_groups=2,
        tabs_per_group={"Active": 3, "Empty": 0},
        top_domains=[("example.com", 3)],
        empty_groups=["Empty"],
    )


def test_text_report_contains_header(sample_stats):
    output = render_stats_text(sample_stats)
    assert "Tab Export Statistics" in output


def test_text_report_contains_total_tabs(sample_stats):
    output = render_stats_text(sample_stats)
    assert "7" in output


def test_text_report_contains_group_names(sample_stats):
    output = render_stats_text(sample_stats)
    assert "Dev" in output
    assert "Reading" in output


def test_text_report_ends_with_newline(sample_stats):
    output = render_stats_text(sample_stats)
    assert output.endswith("\n")


def test_text_report_shows_bar_chart(sample_stats):
    output = render_stats_text(sample_stats)
    assert "#####" in output


def test_markdown_report_contains_h2(sample_stats):
    output = render_stats_markdown(sample_stats)
    assert output.startswith("## Tab Export Statistics")


def test_markdown_report_has_table(sample_stats):
    output = render_stats_markdown(sample_stats)
    assert "|" in output
    assert "Total tabs" in output


def test_markdown_report_top_domains(sample_stats):
    output = render_stats_markdown(sample_stats)
    assert "github.com" in output
    assert "Top Domains" in output


def test_markdown_report_tabs_per_group(sample_stats):
    output = render_stats_markdown(sample_stats)
    assert "Dev" in output
    assert "Reading" in output


def test_markdown_report_empty_group_callout(stats_with_empty_group):
    output = render_stats_markdown(stats_with_empty_group)
    assert "Empty" in output
    assert "Empty groups" in output


def test_markdown_report_no_empty_groups_section(sample_stats):
    output = render_stats_markdown(sample_stats)
    assert "Empty groups" not in output
