"""Tests for tab_export.tagger."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.tagger import TaggingResult, _infer_tags, tag_export


@pytest.fixture()
def sample_export() -> TabExport:
    export = TabExport(source_file="test.txt")
    export._groups = {
        "Dev": [
            Tab(url="https://github.com/user/repo", title="My Repo", group="Dev"),
            Tab(url="https://stackoverflow.com/q/123", title="How to foo", group="Dev"),
        ],
        "Media": [
            Tab(url="https://youtube.com/watch?v=abc", title="Cool Video", group="Media"),
            Tab(url="https://example.com", title="Plain Site", group="Media"),
        ],
    }
    return export


def test_tag_export_returns_tagging_result(sample_export):
    result = tag_export(sample_export)
    assert isinstance(result, TaggingResult)


def test_infer_tags_github():
    tab = Tab(url="https://github.com/foo/bar", title="Repo", group="Dev")
    tags = _infer_tags(tab)
    assert "dev" in tags
    assert "code" in tags


def test_infer_tags_no_match():
    tab = Tab(url="https://example.com", title="Plain Site", group="Other")
    tags = _infer_tags(tab)
    assert tags == []


def test_infer_tags_deduplicates():
    # 'dev' would appear twice if not deduplicated (github + stackoverflow both add 'dev')
    tab = Tab(url="https://github.com", title="stackoverflow tutorial", group="Dev")
    tags = _infer_tags(tab)
    assert tags.count("dev") == 1


def test_tagged_title_contains_tag_brackets(sample_export):
    result = tag_export(sample_export)
    dev_tabs = result.export._groups["Dev"]
    github_tab = next(t for t in dev_tabs if "github" in t.url)
    assert "[dev]" in github_tab.title
    assert "[code]" in github_tab.title


def test_unmatched_tab_title_unchanged(sample_export):
    result = tag_export(sample_export)
    media_tabs = result.export._groups["Media"]
    plain_tab = next(t for t in media_tabs if t.url == "https://example.com")
    assert plain_tab.title == "Plain Site"


def test_tag_counts_populated(sample_export):
    result = tag_export(sample_export)
    assert "dev" in result.tag_counts
    assert result.tag_counts["dev"] >= 1


def test_total_tagged_counts_tabs_with_any_tag(sample_export):
    result = tag_export(sample_export)
    # github, stackoverflow, youtube all match → 3 tabs tagged
    assert result.total_tagged >= 3


def test_source_file_preserved(sample_export):
    result = tag_export(sample_export)
    assert result.export.source_file == "test.txt"


def test_group_structure_preserved(sample_export):
    result = tag_export(sample_export)
    assert set(result.export._groups.keys()) == {"Dev", "Media"}
