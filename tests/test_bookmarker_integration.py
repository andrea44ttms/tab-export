"""Integration tests for the bookmarker pipeline."""
import pytest

from tab_export.bookmarker import classify_bookmarks, BOOKMARK_PATTERNS
from tab_export.parser import Tab, TabExport


def _make_export(urls_and_titles):
    tabs = [
        Tab(title=title, url=url, group="G")
        for url, title in urls_and_titles
    ]
    return TabExport(tabs=tabs)


def test_all_pattern_categories_covered():
    """Every category in BOOKMARK_PATTERNS should be detectable."""
    category_samples = {
        "docs": ("https://docs.python.org/", "Python Docs"),
        "video": ("https://youtube.com/watch?v=1", "Video"),
        "social": ("https://twitter.com/home", "Twitter"),
        "code": ("https://github.com/user/repo", "Repo"),
        "news": ("https://lobste.rs/s/abc", "Lobsters"),
        "shopping": ("https://amazon.com/dp/123", "Product"),
    }
    export = _make_export(list(category_samples.values()))
    result = classify_bookmarks(export)
    found_categories = set(result.by_category().keys())
    for cat in BOOKMARK_PATTERNS:
        assert cat in found_categories, f"Category '{cat}' not detected"


def test_large_export_classification_count():
    pairs = [
        ("https://github.com/a", "Repo A"),
        ("https://github.com/b", "Repo B"),
        ("https://youtube.com/watch?v=1", "Vid 1"),
        ("https://example.com/page", "Page"),
        ("https://example.com/other", "Other"),
    ]
    export = _make_export(pairs)
    result = classify_bookmarks(export)
    # 3 known-category tabs; 2 are "other" and excluded
    assert result.total_classified == 3


def test_by_category_tabs_match_original_tab_objects():
    tab = Tab(title="Repo", url="https://github.com/x/y", group="Dev")
    export = TabExport(tabs=[tab])
    result = classify_bookmarks(export)
    code_tabs = result.by_category().get("code", [])
    assert tab in code_tabs


def test_multi_group_export_all_groups_scanned():
    tabs = [
        Tab(title="Docs", url="https://docs.python.org/", group="G1"),
        Tab(title="Video", url="https://youtube.com/watch?v=2", group="G2"),
    ]
    export = TabExport(tabs=tabs)
    result = classify_bookmarks(export)
    cats = set(result.by_category().keys())
    assert "docs" in cats
    assert "video" in cats
