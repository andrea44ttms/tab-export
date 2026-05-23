"""Tests for tab_export.formatter."""

import pytest

from tab_export.formatter import format_export, format_markdown, format_notion
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def simple_export() -> TabExport:
    tabs = [
        Tab(url="https://python.org", title="Python", group="Dev"),
        Tab(url="https://docs.python.org", title="Docs", group="Dev"),
        Tab(url="https://news.ycombinator.com", title="HN", group="Reading"),
    ]
    return TabExport(tabs=tabs, source_file="test.json")


def test_markdown_contains_group_headings(simple_export: TabExport) -> None:
    result = format_markdown(simple_export)
    assert "## Dev" in result
    assert "## Reading" in result


def test_markdown_contains_links(simple_export: TabExport) -> None:
    result = format_markdown(simple_export)
    assert "[Python](https://python.org)" in result
    assert "[HN](https://news.ycombinator.com)" in result


def test_markdown_ends_with_newline(simple_export: TabExport) -> None:
    result = format_markdown(simple_export)
    assert result.endswith("\n")


def test_notion_uses_h3_headings(simple_export: TabExport) -> None:
    result = format_notion(simple_export)
    assert "### Dev" in result
    assert "### Reading" in result
    assert "## Dev" not in result


def test_notion_contains_links(simple_export: TabExport) -> None:
    result = format_notion(simple_export)
    assert "[Docs](https://docs.python.org)" in result


def test_format_export_dispatches_markdown(simple_export: TabExport) -> None:
    assert format_export(simple_export, fmt="markdown") == format_markdown(simple_export)


def test_format_export_dispatches_notion(simple_export: TabExport) -> None:
    assert format_export(simple_export, fmt="notion") == format_notion(simple_export)


def test_format_export_unknown_format_raises(simple_export: TabExport) -> None:
    with pytest.raises(ValueError, match="Unknown format"):
        format_export(simple_export, fmt="csv")  # type: ignore[arg-type]


def test_tab_without_title_falls_back_to_url() -> None:
    tabs = [Tab(url="https://example.com", title="", group="Misc")]
    export = TabExport(tabs=tabs, source_file=None)
    result = format_markdown(export)
    assert "[https://example.com](https://example.com)" in result
