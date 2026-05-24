"""Tests for tab_export.archiver."""

import json
from pathlib import Path

import pytest

from tab_export.archiver import (
    archive_export,
    load_archive,
    ArchiveResult,
    ArchiveEntry,
    ARCHIVE_FILENAME,
)
from tab_export.parser import Tab, TabExport


@pytest.fixture
def sample_export():
    tabs = [
        Tab(group="Work", title="GitHub", url="https://github.com"),
        Tab(group="Work", title="Jira", url="https://jira.example.com"),
        Tab(group="Reading", title="HN", url="https://news.ycombinator.com"),
    ]
    return TabExport(tabs=tabs, source_file=Path("export.txt"))


def test_archive_export_returns_archive_result(tmp_path, sample_export):
    result = archive_export(sample_export, tmp_path)
    assert isinstance(result, ArchiveResult)


def test_archive_creates_file(tmp_path, sample_export):
    archive_export(sample_export, tmp_path)
    assert (tmp_path / ARCHIVE_FILENAME).exists()


def test_archive_entry_has_correct_counts(tmp_path, sample_export):
    result = archive_export(sample_export, tmp_path)
    assert result.entry.group_count == 2
    assert result.entry.tab_count == 3


def test_archive_entry_has_timestamp(tmp_path, sample_export):
    result = archive_export(sample_export, tmp_path)
    assert result.entry.timestamp  # non-empty string
    assert "T" in result.entry.timestamp  # ISO format


def test_archive_entry_records_source_file(tmp_path, sample_export):
    result = archive_export(sample_export, tmp_path)
    assert result.entry.source_file == "export.txt"


def test_archive_entry_groups_contain_tabs(tmp_path, sample_export):
    result = archive_export(sample_export, tmp_path)
    assert "Work" in result.entry.groups
    work_tabs = result.entry.groups["Work"]
    urls = [t["url"] for t in work_tabs]
    assert "https://github.com" in urls


def test_multiple_archives_accumulate(tmp_path, sample_export):
    archive_export(sample_export, tmp_path)
    archive_export(sample_export, tmp_path)
    result = archive_export(sample_export, tmp_path)
    assert result.total_entries == 3


def test_load_archive_returns_entries(tmp_path, sample_export):
    archive_export(sample_export, tmp_path)
    entries = load_archive(tmp_path)
    assert len(entries) == 1
    assert isinstance(entries[0], ArchiveEntry)


def test_load_archive_empty_dir(tmp_path):
    entries = load_archive(tmp_path)
    assert entries == []


def test_archive_creates_dir_if_missing(tmp_path, sample_export):
    nested = tmp_path / "deep" / "nested"
    archive_export(sample_export, nested)
    assert (nested / ARCHIVE_FILENAME).exists()


def test_archive_file_is_valid_json(tmp_path, sample_export):
    archive_export(sample_export, tmp_path)
    raw = (tmp_path / ARCHIVE_FILENAME).read_text()
    data = json.loads(raw)
    assert isinstance(data, list)
    assert len(data) == 1
