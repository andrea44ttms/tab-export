"""Tests for tab_export.highlighter."""

import pytest

from tab_export.highlighter import HighlightOptions, HighlightResult, highlight_export
from tab_export.parser import Tab, TabExport


@pytest.fixture
def sample_export():
    data = {
        "Work": [
            Tab(title="GitHub Pull Requests", url="https://github.com/pulls", group="Work"),
            Tab(title="Jira Board", url="https://jira.example.com/board", group="Work"),
        ],
        "Reading": [
            Tab(title="Python Docs", url="https://docs.python.org", group="Reading"),
            Tab(title="Real Python", url="https://realpython.com", group="Reading"),
        ],
    }
    return TabExport(source_file="test.txt", _data=data)


def test_highlight_returns_highlight_result(sample_export):
    opts = HighlightOptions(keywords=["github"])
    result = highlight_export(sample_export, opts)
    assert isinstance(result, HighlightResult)


def test_no_keywords_leaves_export_unchanged(sample_export):
    opts = HighlightOptions(keywords=[])
    result = highlight_export(sample_export, opts)
    assert result.total_highlighted == 0
    assert result.was_highlighted is False
    assert result.export is sample_export


def test_keyword_highlights_title(sample_export):
    opts = HighlightOptions(keywords=["GitHub"])
    result = highlight_export(sample_export, opts)
    work_tabs = list(result.export.tabs_in_group("Work"))
    assert "**GitHub**" in work_tabs[0].title


def test_keyword_match_is_case_insensitive(sample_export):
    opts = HighlightOptions(keywords=["python"])
    result = highlight_export(sample_export, opts)
    reading_tabs = list(result.export.tabs_in_group("Reading"))
    assert "**Python**" in reading_tabs[0].title or "**python**" in reading_tabs[0].title.lower()


def test_keyword_highlights_url(sample_export):
    opts = HighlightOptions(keywords=["github"])
    result = highlight_export(sample_export, opts)
    work_tabs = list(result.export.tabs_in_group("Work"))
    assert "**github**" in work_tabs[0].url.lower()


def test_total_highlighted_count(sample_export):
    opts = HighlightOptions(keywords=["python"])
    result = highlight_export(sample_export, opts)
    # "Python Docs" title + docs.python.org url + "Real Python" title + realpython.com url
    assert result.total_highlighted == 2


def test_was_highlighted_true_when_matches(sample_export):
    opts = HighlightOptions(keywords=["jira"])
    result = highlight_export(sample_export, opts)
    assert result.was_highlighted is True


def test_was_highlighted_false_when_no_matches(sample_export):
    opts = HighlightOptions(keywords=["nonexistent_xyz"])
    result = highlight_export(sample_export, opts)
    assert result.was_highlighted is False


def test_custom_markers(sample_export):
    opts = HighlightOptions(keywords=["Jira"], marker_open="==", marker_close="==")
    result = highlight_export(sample_export, opts)
    work_tabs = list(result.export.tabs_in_group("Work"))
    assert "==Jira==" in work_tabs[1].title


def test_groups_preserved_after_highlight(sample_export):
    opts = HighlightOptions(keywords=["github"])
    result = highlight_export(sample_export, opts)
    assert set(result.export.groups()) == {"Work", "Reading"}


def test_unmatched_tabs_are_unchanged(sample_export):
    opts = HighlightOptions(keywords=["github"])
    result = highlight_export(sample_export, opts)
    reading_tabs = list(result.export.tabs_in_group("Reading"))
    assert reading_tabs[0].title == "Python Docs"
    assert reading_tabs[1].title == "Real Python"
