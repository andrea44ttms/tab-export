"""Tests for tab_export.pinner."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.pinner import PinRule, PinningResult, pin_export


@pytest.fixture()
def sample_export() -> TabExport:
    tabs = [
        Tab(title="GitHub Repo", url="https://github.com/org/repo", group="Dev"),
        Tab(title="Python Docs", url="https://docs.python.org", group="Dev"),
        Tab(title="News Feed", url="https://news.ycombinator.com", group="Reading"),
        Tab(title="Stack Overflow", url="https://stackoverflow.com/q/1", group="Reading"),
    ]
    return TabExport(tabs=tabs)


def test_pin_export_returns_pinning_result(sample_export):
    result = pin_export(sample_export, rules=[])
    assert isinstance(result, PinningResult)


def test_no_rules_pins_nothing(sample_export):
    result = pin_export(sample_export, rules=[])
    assert result.total_pinned == 0


def test_no_rules_leaves_titles_unchanged(sample_export):
    result = pin_export(sample_export, rules=[])
    original_titles = [t.title for t in sample_export.tabs]
    new_titles = [t.title for t in result.export.tabs]
    assert new_titles == original_titles


def test_keyword_rule_pins_matching_title(sample_export):
    rules = [PinRule(keyword="GitHub")]
    result = pin_export(sample_export, rules=rules)
    assert result.total_pinned == 1
    pinned_tab = next(t for t in result.export.tabs if "GitHub" in t.title)
    assert pinned_tab.title.startswith("📌")


def test_keyword_rule_is_case_insensitive(sample_export):
    rules = [PinRule(keyword="github")]
    result = pin_export(sample_export, rules=rules)
    assert result.total_pinned == 1


def test_url_field_match(sample_export):
    rules = [PinRule(keyword="stackoverflow", match_field="url")]
    result = pin_export(sample_export, rules=rules)
    assert result.total_pinned == 1
    pinned_tab = next(t for t in result.export.tabs if "Stack" in t.title)
    assert pinned_tab.title.startswith("📌")


def test_title_field_only_skips_url_match(sample_export):
    # "docs" appears in url but not title for the Python Docs tab
    rules = [PinRule(keyword="docs.python", match_field="title")]
    result = pin_export(sample_export, rules=rules)
    assert result.total_pinned == 0


def test_pinned_urls_list_contains_correct_url(sample_export):
    rules = [PinRule(keyword="GitHub")]
    result = pin_export(sample_export, rules=rules)
    assert "https://github.com/org/repo" in result.pinned_urls


def test_already_pinned_tab_not_double_marked():
    tabs = [Tab(title="📌 Already Pinned", url="https://example.com", group="G")]
    export = TabExport(tabs=tabs)
    rules = [PinRule(keyword="Already")]
    result = pin_export(export, rules=rules)
    assert result.export.tabs[0].title.count("📌") == 1


def test_custom_pin_marker(sample_export):
    rules = [PinRule(keyword="GitHub")]
    result = pin_export(sample_export, rules=rules, pin_marker="⭐")
    pinned_tab = next(t for t in result.export.tabs if "GitHub" in t.title)
    assert pinned_tab.title.startswith("⭐")


def test_groups_preserved_after_pinning(sample_export):
    rules = [PinRule(keyword="GitHub")]
    result = pin_export(sample_export, rules=rules)
    groups = result.export.groups()
    assert set(groups.keys()) == {"Dev", "Reading"}


def test_total_tabs_unchanged(sample_export):
    rules = [PinRule(keyword="GitHub")]
    result = pin_export(sample_export, rules=rules)
    assert len(result.export.tabs) == len(sample_export.tabs)
