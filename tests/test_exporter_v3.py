"""Tests for the batch export pipeline (exporter_v3)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tab_export.exporter_v3 import BatchOptions, BatchResult, run_batch
from tab_export.parser import TabExport
from tab_export.parser import Tab


def _make_export(groups: dict) -> TabExport:
    """Build a TabExport directly from a {group: [Tab, ...]} dict."""
    export = TabExport(source_file=Path("test.txt"))
    for group, tabs in groups.items():
        export._groups.append(group)  # type: ignore[attr-defined]
        export._tabs[group] = list(tabs)  # type: ignore[attr-defined]
    return export


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_tab_files(tmp_path: Path):
    file_a = tmp_path / "a.txt"
    file_a.write_text(
        "Work\n"
        "https://example.com | Example Site\n"
        "https://github.com | GitHub\n"
    )
    file_b = tmp_path / "b.txt"
    file_b.write_text(
        "Personal\n"
        "https://news.ycombinator.com | Hacker News\n"
        "https://example.com | Example Site\n"  # duplicate of file_a
    )
    return file_a, file_b


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_run_batch_returns_batch_result(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b]))
    assert isinstance(result, BatchResult)


def test_files_processed_count(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b]))
    assert result.files_processed == 2


def test_output_is_nonempty(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b]))
    assert len(result.output) > 0


def test_deduplication_removes_cross_file_duplicate(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b], deduplicate_across=True))
    assert result.duplicates_removed >= 1
    assert result.tabs_after < result.tabs_before


def test_no_dedup_leaves_duplicates(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b], deduplicate_across=False))
    assert result.duplicates_removed == 0
    assert result.tabs_after == result.tabs_before


def test_notion_format_uses_h3(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b], fmt="notion"))
    assert "### " in result.output


def test_markdown_format_uses_h2(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b], fmt="markdown"))
    assert "## " in result.output


def test_empty_input_raises(tmp_path):
    with pytest.raises(ValueError, match="At least one"):
        run_batch(BatchOptions(input_files=[]))


def test_was_deduplicated_property(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b], deduplicate_across=True))
    assert result.was_deduplicated is (result.duplicates_removed > 0)


def test_summary_contains_files_processed(two_tab_files):
    a, b = two_tab_files
    result = run_batch(BatchOptions(input_files=[a, b]))
    assert "2" in result.summary()
