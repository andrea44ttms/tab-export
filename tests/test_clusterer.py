"""Tests for tab_export.clusterer."""
import pytest

from tab_export.clusterer import (
    ClusteringResult,
    _UNCATEGORISED,
    cluster_tabs,
)
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def sample_export() -> TabExport:
    raw = {
        "Work": [
            Tab(title="GitHub repo", url="https://github.com/user/repo", group="Work"),
            Tab(title="BBC News", url="https://www.bbc.co.uk/news", group="Work"),
            Tab(title="My personal page", url="https://example.com/personal", group="Work"),
        ],
        "Media": [
            Tab(title="Watch later", url="https://www.youtube.com/watch?v=abc", group="Media"),
            Tab(title="Amazon cart", url="https://www.amazon.com/cart", group="Media"),
        ],
    }
    return TabExport(raw_groups=raw)


def test_cluster_returns_clustering_result(sample_export):
    result = cluster_tabs(sample_export)
    assert isinstance(result, ClusteringResult)


def test_cluster_map_covers_all_tabs(sample_export):
    result = cluster_tabs(sample_export)
    all_urls = [
        tab.url
        for tabs in sample_export.groups.values()
        for tab in tabs
    ]
    assert set(result.cluster_map.keys()) == set(all_urls)


def test_github_tab_clustered_as_development(sample_export):
    result = cluster_tabs(sample_export)
    github_url = "https://github.com/user/repo"
    assert result.cluster_map[github_url] == "Development"


def test_bbc_tab_clustered_as_news(sample_export):
    result = cluster_tabs(sample_export)
    assert result.cluster_map["https://www.bbc.co.uk/news"] == "News"


def test_youtube_tab_clustered_as_video(sample_export):
    result = cluster_tabs(sample_export)
    assert result.cluster_map["https://www.youtube.com/watch?v=abc"] == "Video"


def test_amazon_tab_clustered_as_shopping(sample_export):
    result = cluster_tabs(sample_export)
    assert result.cluster_map["https://www.amazon.com/cart"] == "Shopping"


def test_unknown_tab_is_uncategorised(sample_export):
    result = cluster_tabs(sample_export)
    assert result.cluster_map["https://example.com/personal"] == _UNCATEGORISED


def test_total_clustered_excludes_uncategorised(sample_export):
    result = cluster_tabs(sample_export)
    # 4 out of 5 tabs have a named cluster
    assert result.total_clustered == 4


def test_cluster_counts_sums_correctly(sample_export):
    result = cluster_tabs(sample_export)
    total = sum(result.cluster_counts.values())
    assert total == 5


def test_note_prefixed_with_cluster_label(sample_export):
    result = cluster_tabs(sample_export)
    for tabs in result.export.groups.values():
        for tab in tabs:
            assert tab.note is not None
            assert tab.note.startswith("[")


def test_existing_note_preserved(sample_export):
    raw = {
        "G": [
            Tab(title="GitHub", url="https://github.com/x", group="G", note="important")
        ]
    }
    export = TabExport(raw_groups=raw)
    result = cluster_tabs(export)
    tab = result.export.groups["G"][0]
    assert "important" in tab.note
    assert "[Development]" in tab.note


def test_groups_preserved_in_output(sample_export):
    result = cluster_tabs(sample_export)
    assert set(result.export.groups.keys()) == {"Work", "Media"}
