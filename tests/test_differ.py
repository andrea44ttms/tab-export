"""Tests for tab_export.differ."""

from __future__ import annotations

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.differ import DiffResult, diff_exports


def _make_export(groups: dict) -> TabExport:
    """Build a TabExport from {group_name: [(title, url), ...]}."""
    tabs: list[Tab] = []
    for group, entries in groups.items():
        for title, url in entries:
            tabs.append(Tab(title=title, url=url, group=group))
    return TabExport(tabs=tabs, source_file="test.txt")


@pytest.fixture
def before():
    return _make_export({
        "Work": [
            ("GitHub", "https://github.com"),
            ("Jira", "https://jira.example.com"),
        ],
        "News": [
            ("Hacker News", "https://news.ycombinator.com"),
        ],
    })


@pytest.fixture
def after():
    return _make_export({
        "Work": [
            ("GitHub", "https://github.com"),
            ("Confluence", "https://confluence.example.com"),
        ],
        "Personal": [
            ("Reddit", "https://reddit.com"),
        ],
    })


def test_diff_returns_diff_result(before, after):
    result = diff_exports(before, after)
    assert isinstance(result, DiffResult)


def test_added_count(before, after):
    result = diff_exports(before, after)
    assert result.added_count == 2  # Confluence + Reddit


def test_removed_count(before, after):
    result = diff_exports(before, after)
    assert result.removed_count == 2  # Jira + Hacker News


def test_unchanged_count(before, after):
    result = diff_exports(before, after)
    assert result.unchanged_count == 1  # GitHub


def test_has_changes_true(before, after):
    result = diff_exports(before, after)
    assert result.has_changes is True


def test_has_changes_false_when_identical(before):
    result = diff_exports(before, before)
    assert result.has_changes is False


def test_text_contains_group_headings(before, after):
    result = diff_exports(before, after)
    assert "## Work" in result.text
    assert "## News" in result.text
    assert "## Personal" in result.text


def test_removed_line_prefixed_with_minus(before, after):
    result = diff_exports(before, after)
    assert any(line.startswith("- ") and "Jira" in line for line in result.lines)


def test_added_line_prefixed_with_plus(before, after):
    result = diff_exports(before, after)
    assert any(line.startswith("+ ") and "Confluence" in line for line in result.lines)


def test_unchanged_line_prefixed_with_space(before, after):
    result = diff_exports(before, after)
    assert any(line.startswith("  ") and "GitHub" in line for line in result.lines)


def test_summary_contains_counts(before, after):
    result = diff_exports(before, after)
    summary = result.summary()
    assert "+2" in summary
    assert "-2" in summary
    assert "1 unchanged" in summary


def test_empty_exports_produce_no_lines():
    empty = _make_export({})
    result = diff_exports(empty, empty)
    assert result.lines == []
    assert result.has_changes is False
