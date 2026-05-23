"""Tests for tab_export.filter."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.filter import FilterOptions, FilterResult, filter_export


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        source_file="test.txt",
        raw_groups={
            "Work": [
                Tab(title="GitHub Repo", url="https://github.com/org/repo"),
                Tab(title="CI Dashboard", url="https://ci.example.com/builds"),
            ],
            "Reading": [
                Tab(title="Python Docs", url="https://docs.python.org/3/"),
                Tab(title="Real Python", url="https://realpython.com/articles"),
            ],
            "Shopping": [
                Tab(title="Buy Keyboard", url="https://shop.example.com/keyboards"),
            ],
        },
    )


def test_filter_result_type(sample_export):
    result = filter_export(sample_export, FilterOptions())
    assert isinstance(result, FilterResult)


def test_no_filters_keeps_all_tabs(sample_export):
    result = filter_export(sample_export, FilterOptions())
    total = sum(len(t) for t in result.export.groups.values())
    assert total == 5
    assert result.removed_count == 0


def test_keyword_filter_matches_title(sample_export):
    result = filter_export(sample_export, FilterOptions(keyword="python"))
    kept = list(result.export.groups.get("Reading", []))
    titles = [t.title for t in kept]
    assert "Python Docs" in titles
    assert "Real Python" in titles
    assert result.removed_count == 3


def test_keyword_filter_matches_url(sample_export):
    result = filter_export(sample_export, FilterOptions(keyword="github"))
    work_tabs = result.export.groups.get("Work", [])
    assert len(work_tabs) == 1
    assert work_tabs[0].title == "GitHub Repo"


def test_url_pattern_filter(sample_export):
    result = filter_export(sample_export, FilterOptions(url_pattern=r"\.org"))
    all_tabs = [t for tabs in result.export.groups.values() for t in tabs]
    assert all(".org" in t.url for t in all_tabs)


def test_group_name_filter_keeps_only_matching_group(sample_export):
    result = filter_export(sample_export, FilterOptions(group_name="Work"))
    assert "Work" in result.export.groups
    assert result.export.groups["Work"]  # not empty
    # Other groups should be absent (removed, not empty-listed)
    assert "Reading" not in result.export.groups
    assert result.removed_count == 3


def test_exclude_groups_removes_group(sample_export):
    result = filter_export(sample_export, FilterOptions(exclude_groups=["Shopping"]))
    assert "Shopping" not in result.export.groups
    assert result.removed_count == 1


def test_exclude_groups_case_insensitive(sample_export):
    result = filter_export(sample_export, FilterOptions(exclude_groups=["WORK", "shopping"]))
    assert "Work" not in result.export.groups
    assert "Shopping" not in result.export.groups
    assert result.removed_count == 3


def test_combined_keyword_and_exclude(sample_export):
    opts = FilterOptions(keyword="docs", exclude_groups=["Work"])
    result = filter_export(sample_export, opts)
    all_tabs = [t for tabs in result.export.groups.values() for t in tabs]
    assert all("docs" in t.title.lower() or "docs" in t.url.lower() for t in all_tabs)
