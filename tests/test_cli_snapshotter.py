"""Tests for tab_export.cli_snapshotter."""
import argparse
import pytest
from tab_export.parser import Tab, TabExport
from tab_export.cli_snapshotter import (
    add_snapshotter_args,
    build_session,
    render_session_summary,
)
from tab_export.snapshotter import diff_session


def _make_export(*titles: str) -> TabExport:
    tabs = [Tab(title=t, url=f"https://example.com/{i}") for i, t in enumerate(titles)]
    return TabExport(groups={"Group": tabs}, source_file="test.txt")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_snapshotter_args(p)
    return p


def test_add_snapshotter_args_registers_snapshot(parser):
    args = parser.parse_args(["--snapshot", "a.txt"])
    assert "a.txt" in args.snapshot_files


def test_add_snapshotter_args_registers_baseline(parser):
    args = parser.parse_args(["--baseline", "base.txt"])
    assert args.baseline_file == "base.txt"


def test_add_snapshotter_args_show_diff_default_false(parser):
    args = parser.parse_args([])
    assert args.show_diff is False


def test_add_snapshotter_args_show_diff_flag(parser):
    args = parser.parse_args(["--show-diff"])
    assert args.show_diff is True


def test_build_session_no_baseline():
    exports = [_make_export("A"), _make_export("A", "B")]
    session = build_session(exports, ["v1", "v2"])
    assert session.baseline is None
    assert len(session.snapshots) == 2


def test_build_session_with_baseline():
    baseline = _make_export("A")
    exports = [_make_export("A", "B")]
    session = build_session(exports, ["v1"], baseline=baseline)
    assert session.baseline is not None
    assert session.baseline.label == "baseline"


def test_render_session_summary_contains_header():
    exports = [_make_export("A"), _make_export("A", "B")]
    session = build_session(exports, ["v1", "v2"])
    result = diff_session(session)
    summary = render_session_summary(result)
    assert "Snapshot Diff Summary" in summary


def test_render_session_summary_contains_snapshot_label():
    exports = [_make_export("A"), _make_export("A", "B")]
    session = build_session(exports, ["snap-one", "snap-two"])
    result = diff_session(session)
    summary = render_session_summary(result)
    assert "snap-two" in summary


def test_render_session_summary_no_changes_message():
    export = _make_export("Alpha", "Beta")
    baseline = _make_export("Alpha", "Beta")
    session = build_session([_make_export("Alpha", "Beta")], ["v1"], baseline=baseline)
    result = diff_session(session)
    summary = render_session_summary(result)
    assert "No changes" in summary
