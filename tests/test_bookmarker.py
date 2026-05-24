"""Tests for tab_export.bookmarker."""
import pytest

from tab_export.bookmarker import (
    BookmarkResult,
    BookmarkClassification,
    classify_bookmarks,
    _classify_tab,
)
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def sample_export() -> TabExport:
    tabs = [
        Tab(title="Python Docs", url="https://docs.python.org/3/", group="Dev"),
        Tab(title="My Repo", url="https://github.com/user/repo", group="Dev"),
        Tab(title="Funny Cat Video", url="https://youtube.com/watch?v=abc", group="Fun"),
        Tab(title="Twitter Feed", url="https://twitter.com/home", group="Social"),
        Tab(title="Random Blog", url="https://example.com/blog", group="Other"),
    ]
    return TabExport(tabs=tabs)


def test_classify_bookmarks_returns_bookmark_result(sample_export):
    result = classify_bookmarks(sample_export)
    assert isinstance(result, BookmarkResult)


def test_total_classified_excludes_other(sample_export):
    result = classify_bookmarks(sample_export)
    # 4 tabs match a known category; random blog does not
    assert result.total_classified == 4


def test_by_category_groups_correctly(sample_export):
    result = classify_bookmarks(sample_export)
    by_cat = result.by_category()
    assert "docs" in by_cat
    assert "code" in by_cat
    assert "video" in by_cat
    assert "social" in by_cat
    assert "other" not in by_cat


def test_docs_tab_classified_as_docs():
    tab = Tab(title="Docs", url="https://docs.python.org/", group="G")
    assert _classify_tab(tab) == "docs"


def test_github_tab_classified_as_code():
    tab = Tab(title="Repo", url="https://github.com/user/repo", group="G")
    assert _classify_tab(tab) == "code"


def test_youtube_tab_classified_as_video():
    tab = Tab(title="Video", url="https://youtube.com/watch?v=123", group="G")
    assert _classify_tab(tab) == "video"


def test_unknown_url_returns_other():
    tab = Tab(title="Random", url="https://example.com/page", group="G")
    assert _classify_tab(tab) == "other"


def test_classifications_are_bookmark_classification_instances(sample_export):
    result = classify_bookmarks(sample_export)
    for bc in result.classifications:
        assert isinstance(bc, BookmarkClassification)


def test_empty_export_returns_zero_classified():
    export = TabExport(tabs=[])
    result = classify_bookmarks(export)
    assert result.total_classified == 0
    assert result.by_category() == {}


def test_export_preserved_on_result(sample_export):
    result = classify_bookmarks(sample_export)
    assert result.export is sample_export
