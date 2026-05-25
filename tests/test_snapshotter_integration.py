"""Integration tests: snapshotter + cli_snapshotter working together."""
import pytest
from tab_export.parser import Tab, TabExport
from tab_export.snapshotter import SnapshotSession, diff_session
from tab_export.cli_snapshotter import build_session, render_session_summary


def _make_export(group: str, *titles: str) -> TabExport:
    tabs = [Tab(title=t, url=f"https://example.com/{t}") for t in titles]
    return TabExport(groups={group: tabs}, source_file="test.txt")


def test_full_workflow_baseline_plus_two_snapshots():
    baseline = _make_export("Work", "Inbox", "Dashboard")
    v1 = _make_export("Work", "Inbox", "Dashboard", "New Tab")
    v2 = _make_export("Work", "Dashboard")
    session = build_session([v1, v2], ["v1", "v2"], baseline=baseline)
    result = diff_session(session)
    assert result.total_snapshots == 2
    assert result.any_changes is True


def test_render_summary_lists_all_snapshot_labels():
    baseline = _make_export("Research", "Paper A")
    v1 = _make_export("Research", "Paper A", "Paper B")
    v2 = _make_export("Research", "Paper B")
    session = build_session([v1, v2], ["week-1", "week-2"], baseline=baseline)
    result = diff_session(session)
    summary = render_session_summary(result)
    assert "week-1" in summary
    assert "week-2" in summary


def test_identical_snapshots_report_no_changes():
    export = _make_export("Dev", "GitHub", "Docs")
    session = build_session(
        [_make_export("Dev", "GitHub", "Docs")],
        ["copy"],
        baseline=export,
    )
    result = diff_session(session)
    assert result.any_changes is False
    summary = render_session_summary(result)
    assert "No changes" in summary


def test_sequential_diffs_without_baseline():
    exports = [
        _make_export("G", "A"),
        _make_export("G", "A", "B"),
        _make_export("G", "A", "B", "C"),
    ]
    labels = ["s1", "s2", "s3"]
    session = build_session(exports, labels)
    result = diff_session(session)
    assert len(result.diffs) == 3
