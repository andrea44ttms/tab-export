"""Tests for tab_export.cli_archiver."""

import argparse
from pathlib import Path

import pytest

from tab_export.cli_archiver import (
    add_archive_args,
    maybe_archive,
    render_archive_history,
    handle_show_archive,
)
from tab_export.archiver import archive_export, ARCHIVE_FILENAME
from tab_export.parser import Tab, TabExport


@pytest.fixture
def sample_export():
    tabs = [
        Tab(group="Dev", title="PyPI", url="https://pypi.org"),
        Tab(group="Dev", title="Docs", url="https://docs.python.org"),
    ]
    return TabExport(tabs=tabs, source_file=Path("test.txt"))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"archive_dir": None, "show_archive": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_archive_args_registers_options():
    p = argparse.ArgumentParser()
    add_archive_args(p)
    args = p.parse_args([])
    assert hasattr(args, "archive_dir")
    assert hasattr(args, "show_archive")


def test_maybe_archive_does_nothing_without_dir(sample_export, capsys):
    args = _make_args(archive_dir=None)
    maybe_archive(sample_export, args)  # should not raise
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_archive_creates_file(tmp_path, sample_export, capsys):
    args = _make_args(archive_dir=str(tmp_path))
    maybe_archive(sample_export, args)
    assert (tmp_path / ARCHIVE_FILENAME).exists()


def test_maybe_archive_prints_confirmation(tmp_path, sample_export, capsys):
    args = _make_args(archive_dir=str(tmp_path))
    maybe_archive(sample_export, args)
    out = capsys.readouterr().out
    assert "[archive]" in out
    assert "2 tabs" in out


def test_render_archive_history_no_entries(tmp_path):
    result = render_archive_history(tmp_path)
    assert "No archive entries" in result


def test_render_archive_history_shows_entries(tmp_path, sample_export):
    archive_export(sample_export, tmp_path)
    archive_export(sample_export, tmp_path)
    result = render_archive_history(tmp_path)
    assert "2 entries" in result
    assert "2 tabs" in result


def test_handle_show_archive_false_when_flag_not_set(sample_export):
    args = _make_args(show_archive=False)
    assert handle_show_archive(args) is False


def test_handle_show_archive_true_with_flag_and_dir(tmp_path, sample_export, capsys):
    archive_export(sample_export, tmp_path)
    args = _make_args(show_archive=True, archive_dir=str(tmp_path))
    result = handle_show_archive(args)
    assert result is True
    out = capsys.readouterr().out
    assert "Archive history" in out


def test_handle_show_archive_error_without_dir(capsys):
    args = _make_args(show_archive=True, archive_dir=None)
    result = handle_show_archive(args)
    assert result is True
    out = capsys.readouterr().out
    assert "Error" in out
