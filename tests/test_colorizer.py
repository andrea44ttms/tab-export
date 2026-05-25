"""Tests for tab_export.colorizer."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.colorizer import (
    ColorRule,
    ColorizingResult,
    colorize_export,
    render_colorized_text,
    ANSI_COLORS,
)


@pytest.fixture
def sample_export():
    tabs = [
        Tab(title="GitHub Repo", url="https://github.com/user/repo"),
        Tab(title="Python Docs", url="https://docs.python.org/3/"),
        Tab(title="OpenAI Blog", url="https://openai.com/blog"),
        Tab(title="YouTube Video", url="https://youtube.com/watch?v=abc"),
    ]
    return TabExport(
        groups_data={"Work": tabs[:2], "Leisure": tabs[2:]},
        source_file="test.txt",
    )


def test_colorize_returns_colorizing_result(sample_export):
    result = colorize_export(sample_export, [])
    assert isinstance(result, ColorizingResult)


def test_no_rules_produces_empty_color_map(sample_export):
    result = colorize_export(sample_export, [])
    assert result.color_map == {}
    assert result.total_colorized == 0


def test_keyword_rule_colorizes_matching_title(sample_export):
    rules = [ColorRule(keyword="github", color="green")]
    result = colorize_export(sample_export, rules)
    assert "https://github.com/user/repo" in result.color_map
    assert result.color_map["https://github.com/user/repo"] == "green"


def test_keyword_rule_url_field_matches(sample_export):
    rules = [ColorRule(keyword="youtube", color="red", match_field="url")]
    result = colorize_export(sample_export, rules)
    assert "https://youtube.com/watch?v=abc" in result.color_map


def test_keyword_rule_both_field_matches_url(sample_export):
    rules = [ColorRule(keyword="openai", color="cyan", match_field="both")]
    result = colorize_export(sample_export, rules)
    assert "https://openai.com/blog" in result.color_map


def test_total_colorized_counts_correctly(sample_export):
    rules = [
        ColorRule(keyword="github", color="green"),
        ColorRule(keyword="docs", color="blue"),
    ]
    result = colorize_export(sample_export, rules)
    assert result.total_colorized == 2


def test_first_matching_rule_wins(sample_export):
    rules = [
        ColorRule(keyword="github", color="green"),
        ColorRule(keyword="github", color="red"),
    ]
    result = colorize_export(sample_export, rules)
    assert result.color_map.get("https://github.com/user/repo") == "green"


def test_invalid_color_is_skipped(sample_export):
    rules = [ColorRule(keyword="github", color="ultraviolet")]
    result = colorize_export(sample_export, rules)
    assert "https://github.com/user/repo" not in result.color_map


def test_render_colorized_text_contains_ansi_for_match(sample_export):
    rules = [ColorRule(keyword="github", color="green")]
    result = colorize_export(sample_export, rules)
    output = render_colorized_text(result)
    assert ANSI_COLORS["green"] in output
    assert ANSI_COLORS["reset"] in output


def test_render_colorized_text_contains_group_headings(sample_export):
    result = colorize_export(sample_export, [])
    output = render_colorized_text(result)
    assert "## Work" in output
    assert "## Leisure" in output


def test_render_unmatched_tab_has_no_ansi(sample_export):
    rules = [ColorRule(keyword="github", color="green")]
    result = colorize_export(sample_export, rules)
    output = render_colorized_text(result)
    # YouTube line should have no color escape
    for line in output.splitlines():
        if "youtube" in line:
            assert ANSI_COLORS["green"] not in line
