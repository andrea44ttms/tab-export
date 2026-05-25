"""Tests for tab_export.templater."""
from __future__ import annotations

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.templater import (
    DEFAULT_GROUP_TEMPLATE,
    DEFAULT_TAB_TEMPLATE,
    TemplateResult,
    render_template,
)


@pytest.fixture()
def sample_export() -> TabExport:
    tabs = [
        Tab(title="GitHub", url="https://github.com", group="Dev"),
        Tab(title="PyPI", url="https://pypi.org", group="Dev"),
        Tab(title="BBC News", url="https://bbc.co.uk/news", group="News"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


def test_render_template_returns_template_result(sample_export):
    result = render_template(sample_export)
    assert isinstance(result, TemplateResult)


def test_groups_rendered_count(sample_export):
    result = render_template(sample_export)
    assert result.groups_rendered == 2


def test_tabs_rendered_count(sample_export):
    result = render_template(sample_export)
    assert result.tabs_rendered == 3


def test_default_output_contains_group_headings(sample_export):
    result = render_template(sample_export)
    assert "## Dev" in result.rendered
    assert "## News" in result.rendered


def test_default_output_contains_markdown_links(sample_export):
    result = render_template(sample_export)
    assert "[GitHub](https://github.com)" in result.rendered
    assert "[BBC News](https://bbc.co.uk/news)" in result.rendered


def test_rendered_ends_with_newline(sample_export):
    result = render_template(sample_export)
    assert result.rendered.endswith("\n")


def test_line_count_is_positive(sample_export):
    result = render_template(sample_export)
    assert result.line_count > 0


def test_custom_group_template(sample_export):
    result = render_template(sample_export, group_template="=== $group_name ===\n")
    assert "=== Dev ===" in result.rendered
    assert "=== News ===" in result.rendered


def test_custom_tab_template(sample_export):
    result = render_template(sample_export, tab_template="* $url ($title)\n")
    assert "* https://github.com (GitHub)" in result.rendered


def test_custom_separator_appears_between_groups(sample_export):
    result = render_template(sample_export, separator="---\n")
    assert "---" in result.rendered


def test_tags_variable_empty_by_default(sample_export):
    """Tabs without tags should render an empty string for $tags."""
    result = render_template(
        sample_export, tab_template="$title|$tags\n"
    )
    # Each line should have the pipe but an empty tags field
    lines = [l for l in result.rendered.splitlines() if "|" in l]
    assert all(l.endswith("|") for l in lines)


def test_empty_export_renders_empty_string():
    empty = TabExport(tabs=[], source_file="empty.txt")
    result = render_template(empty)
    assert result.groups_rendered == 0
    assert result.tabs_rendered == 0
