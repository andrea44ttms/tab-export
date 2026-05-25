"""Tests for tab_export.snapshotter."""
import pytest
from tab_export.parser import Tab, TabExport
from tab_export.snapshotter import (
    SnapshotSession,
    SnapshotEntry,
    SessionDiffResult,
    diff_session,
)


def _make_export(*titles: str) -> TabExport:
    tabs = [Tab(title=t, url=f"https://example.com/{i}") for i, t in enumerate(titles)]
    return TabExport(groups={"Group": tabs}, source_file="test.txt")


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def session_with_baseline():
    s = SnapshotSession()
    s.set_baseline("v0", _make_export("Alpha", "Beta"))
    s.add("v1", _make_export("Alpha", "Beta", "Gamma"))
    s.add("v2", _make_export("Alpha"))
    return s


@pytest.fixture
def session_no_baseline():
    s = SnapshotSession()
    s.add("v1", _make_export("Alpha"))
    s.add("v2", _make_export("Alpha", "Beta"))
    return s


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_diff_session_returns_session_diff_result(session_with_baseline):
    result = diff_session(session_with_baseline)
    assert isinstance(result, SessionDiffResult)


def test_total_snapshots_matches_added(session_with_baseline):
    result = diff_session(session_with_baseline)
    assert result.total_snapshots == 2


def test_diffs_count_equals_snapshots(session_with_baseline):
    result = diff_session(session_with_baseline)
    assert len(result.diffs) == 2


def test_any_changes_true_when_tabs_differ(session_with_baseline):
    result = diff_session(session_with_baseline)
    assert result.any_changes is True


def test_any_changes_false_when_identical():
    s = SnapshotSession()
    export = _make_export("Alpha", "Beta")
    s.set_baseline("v0", export)
    s.add("v1", _make_export("Alpha", "Beta"))
    result = diff_session(s)
    assert result.any_changes is False


def test_no_baseline_diffs_against_previous(session_no_baseline):
    result = diff_session(session_no_baseline)
    assert len(result.diffs) == 2


def test_empty_session_returns_no_diffs():
    s = SnapshotSession()
    result = diff_session(s)
    assert result.diffs == []
    assert result.total_snapshots == 0


def test_added_tabs_detected_in_diff(session_with_baseline):
    result = diff_session(session_with_baseline)
    # v1 adds Gamma over baseline
    first_diff = result.diffs[0]
    assert first_diff.total_added >= 1


def test_removed_tabs_detected_in_diff(session_with_baseline):
    result = diff_session(session_with_baseline)
    # v2 removes Beta and Gamma vs baseline
    second_diff = result.diffs[1]
    assert second_diff.total_removed >= 1
