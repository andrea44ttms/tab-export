"""Tests for tab_export.truncator."""

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.truncator import TruncateOptions, TruncationResult, truncate_export


@pytest.fixture
def sample_export():
    return TabExport(
        tabs=[
            Tab(title="Short", url="https://example.com", group="G1"),
            Tab(
                title="A very long title that exceeds the limit easily",
                url="https://example.com/some/very/long/path/that/goes/on",
                group="G1",
            ),
            Tab(title="Another tab", url="https://short.io", group="G2"),
        ]
    )


def test_truncate_returns_truncation_result(sample_export):
    result = truncate_export(sample_export, TruncateOptions())
    assert isinstance(result, TruncationResult)


def test_no_limits_leaves_tabs_unchanged(sample_export):
    result = truncate_export(sample_export, TruncateOptions())
    assert result.tabs_truncated == 0
    assert result.was_truncated is False
    for orig, new in zip(sample_export.tabs, result.export.tabs):
        assert new.title == orig.title
        assert new.url == orig.url


def test_title_truncation_applies_ellipsis(sample_export):
    opts = TruncateOptions(max_title_length=10)
    result = truncate_export(sample_export, opts)
    for tab in result.export.tabs:
        assert len(tab.title) <= 10


def test_url_truncation_applies_ellipsis(sample_export):
    opts = TruncateOptions(max_url_length=25)
    result = truncate_export(sample_export, opts)
    for tab in result.export.tabs:
        assert len(tab.url) <= 25


def test_tabs_truncated_count_is_accurate(sample_export):
    opts = TruncateOptions(max_title_length=10)
    result = truncate_export(sample_export, opts)
    # Only the long title tab should be truncated
    assert result.tabs_truncated == 1


def test_was_truncated_true_when_any_tab_changed(sample_export):
    opts = TruncateOptions(max_title_length=10)
    result = truncate_export(sample_export, opts)
    assert result.was_truncated is True


def test_custom_ellipsis(sample_export):
    opts = TruncateOptions(max_title_length=15, ellipsis="...")
    result = truncate_export(sample_export, opts)
    for tab in result.export.tabs:
        assert len(tab.title) <= 15
        if len(tab.title) == 15:
            assert tab.title.endswith("...")


def test_group_preserved_after_truncation(sample_export):
    opts = TruncateOptions(max_title_length=5)
    result = truncate_export(sample_export, opts)
    groups = [t.group for t in result.export.tabs]
    assert groups == ["G1", "G1", "G2"]


def test_source_file_preserved(sample_export):
    export = TabExport(tabs=sample_export.tabs, source_file="my_tabs.txt")
    result = truncate_export(export, TruncateOptions(max_title_length=5))
    assert result.export.source_file == "my_tabs.txt"
