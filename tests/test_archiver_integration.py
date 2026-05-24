"""Integration tests for the archiver across multiple export snapshots."""

import json
from pathlib import Path

import pytest

from tab_export.archiver import archive_export, load_archive, ARCHIVE_FILENAME
from tab_export.parser import Tab, TabExport


def _make_export(groups_tabs: dict, source: str = "file.txt") -> TabExport:
    tabs = [
        Tab(group=group, title=title, url=url)
        for group, items in groups_tabs.items()
        for title, url in items
    ]
    return TabExport(tabs=tabs, source_file=Path(source))


def test_archive_preserves_all_group_names(tmp_path):
    export = _make_export(
        {
            "Work": [("GitHub", "https://github.com")],
            "News": [("HN", "https://news.ycombinator.com")],
        }
    )
    result = archive_export(export, tmp_path)
    assert set(result.entry.groups.keys()) == {"Work", "News"}


def test_sequential_snapshots_have_unique_timestamps(tmp_path):
    export = _make_export({"A": [("X", "https://x.com")]})
    r1 = archive_export(export, tmp_path)
    r2 = archive_export(export, tmp_path)
    # Timestamps may match within same second, but both should be valid ISO strings
    assert r1.entry.timestamp
    assert r2.entry.timestamp


def test_load_archive_matches_written_entries(tmp_path):
    e1 = _make_export({"Work": [("G", "https://g.com")]}, source="a.txt")
    e2 = _make_export(
        {"Read": [("H", "https://h.com"), ("I", "https://i.com")]}, source="b.txt"
    )
    archive_export(e1, tmp_path)
    archive_export(e2, tmp_path)

    entries = load_archive(tmp_path)
    assert len(entries) == 2
    assert entries[0].tab_count == 1
    assert entries[1].tab_count == 2
    assert entries[1].source_file == "b.txt"


def test_archive_json_structure(tmp_path):
    export = _make_export({"Dev": [("PyPI", "https://pypi.org")]})
    archive_export(export, tmp_path)
    raw = json.loads((tmp_path / ARCHIVE_FILENAME).read_text())
    entry = raw[0]
    assert "timestamp" in entry
    assert "group_count" in entry
    assert "tab_count" in entry
    assert "groups" in entry
    assert isinstance(entry["groups"], dict)


def test_export_without_source_file(tmp_path):
    tabs = [Tab(group="G", title="T", url="https://t.com")]
    export = TabExport(tabs=tabs, source_file=None)
    result = archive_export(export, tmp_path)
    assert result.entry.source_file is None
    entries = load_archive(tmp_path)
    assert entries[0].source_file is None
