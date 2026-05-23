"""Tests for tab_export.sorter module."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.sorter import SortKey, SortOptions, SortOrder, sort_export


@pytest.fixture()
def mixed_export() -> TabExport:
    """Export with two groups and unsorted tabs."""
    export = TabExport.__new__(TabExport)
    export.source_file = None
    export._groups = {
        "Zebra Group": [
            Tab(title="Mango", url="https://mango.example.com", group="Zebra Group"),
            Tab(title="Apple", url="https://apple.example.com", group="Zebra Group"),
        ],
        "Alpha Group": [
            Tab(title="Zoo", url="https://zoo.example.com", group="Alpha Group"),
            Tab(title="Banana", url="https://banana.example.com", group="Alpha Group"),
        ],
    }
    return export


def test_sort_tabs_by_title_asc(mixed_export):
    result = sort_export(mixed_export, SortOptions(key=SortKey.TITLE, order=SortOrder.ASC))
    titles = [t.title for t in result.tabs_in_group("Zebra Group")]
    assert titles == ["Apple", "Mango"]


def test_sort_tabs_by_title_desc(mixed_export):
    result = sort_export(mixed_export, SortOptions(key=SortKey.TITLE, order=SortOrder.DESC))
    titles = [t.title for t in result.tabs_in_group("Zebra Group")]
    assert titles == ["Mango", "Apple"]


def test_sort_tabs_by_url(mixed_export):
    result = sort_export(mixed_export, SortOptions(key=SortKey.URL))
    urls = [t.url for t in result.tabs_in_group("Alpha Group")]
    assert urls == ["https://banana.example.com", "https://zoo.example.com"]


def test_sort_groups_alphabetically(mixed_export):
    result = sort_export(mixed_export, SortOptions(sort_groups=True))
    assert result.groups() == ["Alpha Group", "Zebra Group"]


def test_sort_groups_desc(mixed_export):
    result = sort_export(
        mixed_export, SortOptions(sort_groups=True, order=SortOrder.DESC)
    )
    assert result.groups()[0] == "Zebra Group"


def test_sort_by_group_key_sorts_groups(mixed_export):
    result = sort_export(mixed_export, SortOptions(key=SortKey.GROUP))
    assert result.groups() == ["Alpha Group", "Zebra Group"]


def test_original_export_unchanged(mixed_export):
    """sort_export must not mutate the original export."""
    original_groups = list(mixed_export.groups())
    sort_export(mixed_export, SortOptions(sort_groups=True))
    assert list(mixed_export.groups()) == original_groups


def test_default_options_returns_tab_export(mixed_export):
    result = sort_export(mixed_export)
    assert isinstance(result, TabExport)
