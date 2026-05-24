"""Tests for tab_export.comparator."""
import pytest

from tab_export.comparator import ComparisonResult, compare_exports
from tab_export.parser import Tab, TabExport


def _make_export(groups_tabs: dict) -> TabExport:
    """Helper: build a TabExport from {group: [(title, url), ...]}."""
    rows = []
    for group, tabs in groups_tabs.items():
        for title, url in tabs:
            rows.append({"group": group, "title": title, "url": url})
    return TabExport(tabs=[Tab(**r) for r in rows], source_file="test.txt")


@pytest.fixture
def before():
    return _make_export({
        "Work": [("GitHub", "https://github.com"), ("Jira", "https://jira.example.com")],
        "News": [("HN", "https://news.ycombinator.com")],
    })


@pytest.fixture
def after():
    return _make_export({
        "Work": [("GitHub", "https://github.com"), ("Slack", "https://slack.com")],
        "Docs": [("MDN", "https://developer.mozilla.org")],
    })


def test_compare_returns_comparison_result(before, after):
    result = compare_exports(before, after)
    assert isinstance(result, ComparisonResult)


def test_added_tabs_detected(before, after):
    result = compare_exports(before, after)
    added_urls = [t.url for t in result.added_tabs]
    assert "https://slack.com" in added_urls
    assert "https://developer.mozilla.org" in added_urls


def test_removed_tabs_detected(before, after):
    result = compare_exports(before, after)
    removed_urls = [t.url for t in result.removed_tabs]
    assert "https://jira.example.com" in removed_urls
    assert "https://news.ycombinator.com" in removed_urls


def test_unchanged_tab_not_in_added_or_removed(before, after):
    result = compare_exports(before, after)
    all_urls = [t.url for t in result.added_tabs + result.removed_tabs]
    assert "https://github.com" not in all_urls


def test_added_groups_detected(before, after):
    result = compare_exports(before, after)
    assert "Docs" in result.added_groups


def test_removed_groups_detected(before, after):
    result = compare_exports(before, after)
    assert "News" in result.removed_groups


def test_total_added(before, after):
    result = compare_exports(before, after)
    assert result.total_added == 2


def test_total_removed(before, after):
    result = compare_exports(before, after)
    assert result.total_removed == 2


def test_is_unchanged_when_identical(before):
    result = compare_exports(before, before)
    assert result.is_unchanged is True


def test_is_unchanged_false_when_different(before, after):
    result = compare_exports(before, after)
    assert result.is_unchanged is False


def test_summary_lines_contains_added_and_removed(before, after):
    result = compare_exports(before, after)
    lines = result.summary_lines()
    joined = "\n".join(lines)
    assert "Added tabs" in joined
    assert "Removed tabs" in joined


def test_summary_lines_contains_group_names(before, after):
    result = compare_exports(before, after)
    lines = "\n".join(result.summary_lines())
    assert "Docs" in lines
    assert "News" in lines
