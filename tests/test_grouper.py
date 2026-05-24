"""Tests for tab_export.grouper."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.grouper import GroupBy, GroupingResult, group_tabs_by, _extract_key


@pytest.fixture()
def flat_export() -> TabExport:
    """Export where all tabs have no group assigned."""
    return TabExport(
        tabs=[
            Tab(url="https://docs.python.org/3/", title="Python Docs", group=""),
            Tab(url="https://pypi.org/project/requests/", title="requests", group=""),
            Tab(url="https://www.python.org/", title="Python Home", group=""),
            Tab(url="https://news.ycombinator.com/", title="HN", group=""),
            Tab(url="https://github.com/psf/black", title="Black", group=""),
            Tab(url="https://github.com/astral-sh/ruff", title="Ruff", group=""),
        ]
    )


@pytest.fixture()
def mixed_export() -> TabExport:
    """Export where some tabs already have a group."""
    return TabExport(
        tabs=[
            Tab(url="https://docs.python.org/3/", title="Python Docs", group="Python"),
            Tab(url="https://github.com/psf/black", title="Black", group=""),
            Tab(url="https://github.com/astral-sh/ruff", title="Ruff", group=""),
        ]
    )


# --- _extract_key ---

def test_extract_key_domain_strips_www():
    assert _extract_key("https://www.python.org/", GroupBy.DOMAIN) == "python.org"


def test_extract_key_domain_no_www():
    assert _extract_key("https://pypi.org/", GroupBy.DOMAIN) == "pypi.org"


def test_extract_key_subdomain_preserves_subdomain():
    assert _extract_key("https://docs.python.org/", GroupBy.SUBDOMAIN) == "docs.python.org"


def test_extract_key_bad_url_returns_unknown():
    assert _extract_key("not a url", GroupBy.DOMAIN) == "unknown"


# --- group_tabs_by ---

def test_returns_grouping_result(flat_export):
    result = group_tabs_by(flat_export)
    assert isinstance(result, GroupingResult)


def test_all_tabs_preserved(flat_export):
    result = group_tabs_by(flat_export)
    assert len(result.export.tabs) == len(flat_export.tabs)


def test_groups_by_domain(flat_export):
    result = group_tabs_by(flat_export, by=GroupBy.DOMAIN)
    groups = result.export.groups()
    assert "python.org" in groups
    assert "github.com" in groups
    assert "ycombinator.com" in groups
    assert "pypi.org" in groups


def test_github_tabs_in_same_group(flat_export):
    result = group_tabs_by(flat_export, by=GroupBy.DOMAIN)
    github_tabs = result.export.tabs_in_group("github.com")
    assert len(github_tabs) == 2


def test_group_count_reported(flat_export):
    result = group_tabs_by(flat_export, by=GroupBy.DOMAIN)
    assert result.new_group_count == len(result.export.groups())
    assert result.original_group_count == 0  # flat_export has no groups


def test_preserve_existing_keeps_named_groups(mixed_export):
    result = group_tabs_by(mixed_export, by=GroupBy.DOMAIN, preserve_existing=True)
    groups = result.export.groups()
    assert "Python" in groups
    assert "github.com" in groups


def test_preserve_existing_false_overrides_groups(mixed_export):
    result = group_tabs_by(mixed_export, by=GroupBy.DOMAIN, preserve_existing=False)
    groups = result.export.groups()
    assert "Python" not in groups
    assert "python.org" in groups
