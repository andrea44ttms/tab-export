"""Tests for tab_export.cli_bookmarker."""
import argparse
import pytest

from tab_export.cli_bookmarker import (
    add_bookmarker_args,
    render_bookmark_summary,
    apply_bookmark_classification,
)
from tab_export.bookmarker import classify_bookmarks
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        tabs=[
            Tab(title="GitHub Repo", url="https://github.com/user/proj", group="Dev"),
            Tab(title="Watch Later", url="https://youtube.com/watch?v=xyz", group="Fun"),
            Tab(title="Blog Post", url="https://example.com/post", group="Other"),
        ]
    )


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"classify_bookmarks": False, "show_category": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_bookmarker_args_registers_classify_flag():
    parser = argparse.ArgumentParser()
    add_bookmarker_args(parser)
    args = parser.parse_args(["--classify-bookmarks"])
    assert args.classify_bookmarks is True


def test_add_bookmarker_args_registers_show_category():
    parser = argparse.ArgumentParser()
    add_bookmarker_args(parser)
    args = parser.parse_args(["--show-category", "code"])
    assert args.show_category == "code"


def test_render_bookmark_summary_contains_header(sample_export):
    result = classify_bookmarks(sample_export)
    summary = render_bookmark_summary(result)
    assert "Bookmark classification" in summary


def test_render_bookmark_summary_lists_categories(sample_export):
    result = classify_bookmarks(sample_export)
    summary = render_bookmark_summary(result)
    assert "code" in summary
    assert "video" in summary


def test_apply_no_flags_returns_export_unchanged(sample_export):
    args = _make_args()
    returned = apply_bookmark_classification(args, sample_export)
    assert returned is sample_export


def test_apply_show_category_filters_tabs(sample_export):
    args = _make_args(show_category="code")
    filtered = apply_bookmark_classification(args, sample_export)
    assert all("github" in t.url for t in filtered.tabs)


def test_apply_show_unknown_category_returns_empty(sample_export):
    args = _make_args(show_category="shopping")
    filtered = apply_bookmark_classification(args, sample_export)
    assert len(filtered.tabs) == 0


def test_apply_classify_prints_output(sample_export, capsys):
    args = _make_args(classify_bookmarks=True)
    apply_bookmark_classification(args, sample_export)
    captured = capsys.readouterr()
    assert "Bookmark classification" in captured.out
