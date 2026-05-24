"""Tests for tab_export.splitter."""

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.splitter import SplitResult, split_export


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        export={
            "Work": [
                Tab(title="Jira", url="https://jira.example.com"),
                Tab(title="Confluence", url="https://confluence.example.com"),
            ],
            "News": [
                Tab(title="Hacker News", url="https://news.ycombinator.com"),
            ],
            "Shopping": [
                Tab(title="Amazon", url="https://amazon.com"),
                Tab(title="eBay", url="https://ebay.com"),
                Tab(title="Etsy", url="https://etsy.com"),
            ],
        },
        source_file="tabs.txt",
    )


def test_split_returns_split_result(sample_export):
    result = split_export(sample_export, max_tabs=10)
    assert isinstance(result, SplitResult)


def test_no_split_needed_returns_single_chunk(sample_export):
    result = split_export(sample_export, max_tabs=10)
    assert result.total_chunks == 1


def test_chunk_contains_all_tabs_when_no_split(sample_export):
    result = split_export(sample_export, max_tabs=10)
    total = sum(result.chunk_sizes)
    assert total == 6


def test_split_creates_multiple_chunks(sample_export):
    # max 2 tabs per chunk forces splits
    result = split_export(sample_export, max_tabs=2)
    assert result.total_chunks > 1


def test_each_chunk_respects_max_tabs(sample_export):
    max_tabs = 3
    result = split_export(sample_export, max_tabs=max_tabs)
    for size in result.chunk_sizes:
        assert size <= max_tabs


def test_all_tabs_preserved_after_split(sample_export):
    result = split_export(sample_export, max_tabs=2)
    total = sum(result.chunk_sizes)
    assert total == 6


def test_groups_not_broken_across_chunks(sample_export):
    result = split_export(sample_export, max_tabs=3)
    for chunk in result.chunks:
        for group in chunk.groups():
            tabs = list(chunk.tabs_in_group(group))
            original = list(sample_export.tabs_in_group(group))
            assert tabs == original


def test_source_file_preserved_in_chunks(sample_export):
    result = split_export(sample_export, max_tabs=2)
    for chunk in result.chunks:
        assert chunk.source_file == "tabs.txt"


def test_chunk_sizes_property_matches_actual_tabs(sample_export):
    result = split_export(sample_export, max_tabs=3)
    for chunk, reported_size in zip(result.chunks, result.chunk_sizes):
        actual = sum(len(list(chunk.tabs_in_group(g))) for g in chunk.groups())
        assert reported_size == actual


def test_invalid_max_tabs_raises_value_error(sample_export):
    with pytest.raises(ValueError, match="max_tabs"):
        split_export(sample_export, max_tabs=0)


def test_oversized_group_gets_own_chunk():
    big_export = TabExport(
        export={
            "Huge": [Tab(title=f"Tab {i}", url=f"https://example.com/{i}") for i in range(5)],
            "Tiny": [Tab(title="One", url="https://one.com")],
        },
        source_file=None,
    )
    result = split_export(big_export, max_tabs=3)
    group_names = [list(chunk.groups()) for chunk in result.chunks]
    assert any("Huge" in names for names in group_names)
