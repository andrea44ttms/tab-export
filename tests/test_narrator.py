"""Tests for tab_export.narrator."""
from __future__ import annotations

import pytest

from tab_export.parser import TabExport, Tab
from tab_export.narrator import narrate_export, NarrationResult


@pytest.fixture()
def sample_export() -> TabExport:
    raw = (
        "Group: Work\n"
        "  - https://github.com/org/repo | GitHub Repo\n"
        "  - https://docs.python.org | Python Docs\n"
        "Group: Personal\n"
        "  - https://news.ycombinator.com | Hacker News\n"
    )
    return TabExport.parse(raw)


@pytest.fixture()
def single_tab_export() -> TabExport:
    raw = (
        "Group: Solo\n"
        "  - https://example.com | Example\n"
    )
    return TabExport.parse(raw)


def test_narrate_returns_narration_result(sample_export):
    result = narrate_export(sample_export)
    assert isinstance(result, NarrationResult)


def test_text_property_joins_lines(sample_export):
    result = narrate_export(sample_export)
    assert result.text == "\n".join(result.lines)


def test_summary_mentions_tab_count(sample_export):
    result = narrate_export(sample_export)
    assert "3" in result.text


def test_summary_mentions_group_count(sample_export):
    result = narrate_export(sample_export)
    assert "2" in result.text


def test_singular_tab_word(single_tab_export):
    result = narrate_export(single_tab_export)
    assert " 1 tab " in result.text


def test_singular_group_word(single_tab_export):
    result = narrate_export(single_tab_export)
    assert " 1 group" in result.text


def test_verbose_includes_group_breakdown(sample_export):
    result = narrate_export(sample_export, verbose=True)
    assert "Group breakdown:" in result.text
    assert "Work" in result.text
    assert "Personal" in result.text


def test_non_verbose_excludes_group_breakdown(sample_export):
    result = narrate_export(sample_export, verbose=False)
    assert "Group breakdown:" not in result.text


def test_verbose_tab_counts_in_breakdown(sample_export):
    result = narrate_export(sample_export, verbose=True)
    assert "2 tabs" in result.text
    assert "1 tab" in result.text


def test_average_tabs_mentioned(sample_export):
    result = narrate_export(sample_export)
    assert "average" in result.text.lower()
