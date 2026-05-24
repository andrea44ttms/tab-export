"""Tests for tab_export.stats module."""
import pytest
from tab_export.parser import Tab, TabExport
from tab_export.stats import compute_stats, ExportStats, _extract_domain


@pytest.fixture
def sample_export():
    tabs = [
        Tab(title="GitHub", url="https://github.com/user/repo", group="Dev"),
        Tab(title="GitLab", url="https://gitlab.com/project", group="Dev"),
        Tab(title="News", url="https://www.bbc.com/news", group="Reading"),
        Tab(title="More News", url="https://bbc.com/sport", group="Reading"),
        Tab(title="Docs", url="https://docs.python.org/3/", group="Dev"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


@pytest.fixture
def export_with_empty_group():
    tabs = [
        Tab(title="A", url="https://example.com", group="Full"),
    ]
    export = TabExport(tabs=tabs, source_file="test.txt")
    return export


def test_compute_stats_returns_export_stats(sample_export):
    result = compute_stats(sample_export)
    assert isinstance(result, ExportStats)


def test_total_tabs(sample_export):
    result = compute_stats(sample_export)
    assert result.total_tabs == 5


def test_total_groups(sample_export):
    result = compute_stats(sample_export)
    assert result.total_groups == 2


def test_tabs_per_group(sample_export):
    result = compute_stats(sample_export)
    assert result.tabs_per_group["Dev"] == 3
    assert result.tabs_per_group["Reading"] == 2


def test_avg_tabs_per_group(sample_export):
    result = compute_stats(sample_export)
    assert result.avg_tabs_per_group == 2.5


def test_avg_tabs_per_group_zero_groups():
    empty = TabExport(tabs=[], source_file="empty.txt")
    result = compute_stats(empty)
    assert result.avg_tabs_per_group == 0.0


def test_top_domains_strips_www(sample_export):
    result = compute_stats(sample_export)
    domains = dict(result.top_domains)
    assert "bbc.com" in domains
    assert domains["bbc.com"] == 2


def test_top_domains_respects_top_n(sample_export):
    result = compute_stats(sample_export, top_n=1)
    assert len(result.top_domains) == 1


def test_no_empty_groups(sample_export):
    result = compute_stats(sample_export)
    assert result.empty_groups == []


def test_summary_lines_returns_list(sample_export):
    result = compute_stats(sample_export)
    lines = result.summary_lines()
    assert isinstance(lines, list)
    assert any("5" in line for line in lines)


def test_extract_domain_strips_www():
    assert _extract_domain("https://www.example.com/path") == "example.com"


def test_extract_domain_no_www():
    assert _extract_domain("https://github.com/user") == "github.com"


def test_extract_domain_invalid_url():
    assert _extract_domain("not-a-url") == ""
