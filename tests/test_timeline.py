"""Tests for tab_export.timeline."""

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.timeline import TimelineResult, build_timeline, _DEFAULT_LABEL


@pytest.fixture
def sample_export() -> TabExport:
    tabs = [
        Tab(title="Breaking News Today", url="https://news.example.com/breaking", group="News"),
        Tab(title="Weekly Digest", url="https://blog.example.com/weekly", group="Blogs"),
        Tab(title="Monthly Release Notes", url="https://github.com/proj/changelog", group="Dev"),
        Tab(title="Archive of Old Posts", url="https://example.com/archive", group="Misc"),
        Tab(title="Random Tab", url="https://example.com/random", group="Misc"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


def test_build_timeline_returns_timeline_result(sample_export):
    result = build_timeline(sample_export)
    assert isinstance(result, TimelineResult)


def test_today_bucket_contains_breaking_news(sample_export):
    result = build_timeline(sample_export)
    assert "today" in result.buckets
    titles = [t.title for t in result.buckets["today"]]
    assert "Breaking News Today" in titles


def test_this_week_bucket_contains_digest(sample_export):
    result = build_timeline(sample_export)
    assert "this-week" in result.buckets
    titles = [t.title for t in result.buckets["this-week"]]
    assert "Weekly Digest" in titles


def test_this_month_bucket_contains_release_notes(sample_export):
    result = build_timeline(sample_export)
    assert "this-month" in result.buckets
    titles = [t.title for t in result.buckets["this-month"]]
    assert "Monthly Release Notes" in titles


def test_older_bucket_contains_archive(sample_export):
    result = build_timeline(sample_export)
    assert "older" in result.buckets
    titles = [t.title for t in result.buckets["older"]]
    assert "Archive of Old Posts" in titles


def test_uncategorized_bucket_for_unmatched_tabs(sample_export):
    result = build_timeline(sample_export)
    assert _DEFAULT_LABEL in result.buckets
    titles = [t.title for t in result.buckets[_DEFAULT_LABEL]]
    assert "Random Tab" in titles


def test_total_bucketed_excludes_uncategorized(sample_export):
    result = build_timeline(sample_export)
    # today + this-week + this-month + older = 4 tabs
    assert result.total_bucketed == 4


def test_bucket_names_lists_present_buckets(sample_export):
    result = build_timeline(sample_export)
    names = result.bucket_names
    assert "today" in names
    assert _DEFAULT_LABEL in names


def test_summary_lines_contains_header(sample_export):
    result = build_timeline(sample_export)
    lines = result.summary_lines()
    assert lines[0] == "Timeline summary:"


def test_summary_lines_mention_each_bucket(sample_export):
    result = build_timeline(sample_export)
    lines = result.summary_lines()
    combined = "\n".join(lines)
    for name in result.bucket_names:
        assert name in combined


def test_empty_export_produces_empty_buckets():
    export = TabExport(tabs=[], source_file="empty.txt")
    result = build_timeline(export)
    assert result.total_bucketed == 0
    assert result.buckets == {}
