"""Tests for tab_export.notifier."""
from __future__ import annotations

import pytest

from tab_export.notifier import notify, NotificationResult
from tab_export.exporter import PipelineResult


def _make_result(
    tabs_before: int = 10,
    tabs_after: int = 10,
    dedup_removed: int = 0,
    filter_removed: int = 0,
) -> PipelineResult:
    return PipelineResult(
        output="# Group\n- [Tab](https://example.com)\n",
        tabs_before=tabs_before,
        tabs_after=tabs_after,
        dedup_removed=dedup_removed,
        filter_removed=filter_removed,
    )


def test_notify_returns_notification_result():
    result = notify(_make_result())
    assert isinstance(result, NotificationResult)


def test_messages_contain_tabs_before():
    result = notify(_make_result(tabs_before=7, tabs_after=7))
    assert any("7" in m for m in result.messages)


def test_messages_contain_tabs_after():
    result = notify(_make_result(tabs_before=10, tabs_after=8, dedup_removed=2))
    assert any("8" in m for m in result.messages)


def test_dedup_message_present_when_dupes_removed():
    result = notify(_make_result(tabs_before=10, tabs_after=8, dedup_removed=2))
    assert any("duplicate" in m.lower() for m in result.messages)


def test_dedup_message_absent_when_no_dupes():
    result = notify(_make_result())
    assert not any("duplicate" in m.lower() for m in result.messages)


def test_filter_message_present_when_filtered():
    result = notify(_make_result(tabs_before=10, tabs_after=7, filter_removed=3))
    assert any("filter" in m.lower() for m in result.messages)


def test_no_warnings_when_nothing_removed():
    result = notify(_make_result(tabs_before=5, tabs_after=5), warn_threshold=0)
    assert not result.has_warnings


def test_warning_when_tabs_removed_exceeds_threshold():
    result = notify(_make_result(tabs_before=10, tabs_after=5, dedup_removed=5), warn_threshold=2)
    assert result.has_warnings


def test_warning_when_all_tabs_removed():
    result = notify(_make_result(tabs_before=3, tabs_after=0, filter_removed=3))
    assert result.has_warnings
    assert any("empty" in w.lower() for w in result.warnings)


def test_text_property_joins_messages_and_warnings():
    result = notify(_make_result(tabs_before=10, tabs_after=5, dedup_removed=5), warn_threshold=0)
    text = result.text
    assert "[info]" in text


def test_text_contains_warn_prefix_for_warnings():
    result = notify(_make_result(tabs_before=4, tabs_after=0, filter_removed=4))
    assert "[warn]" in result.text


def test_no_warnings_flag_false_by_default_on_clean_run():
    result = notify(_make_result(tabs_before=5, tabs_after=5))
    assert result.has_warnings is False
