"""Tests for tab_export.cli_prioritizer."""
from __future__ import annotations

import argparse

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.cli_prioritizer import (
    add_prioritizer_args,
    apply_prioritizing,
    render_priority_summary,
    _parse_priority_rules,
)
from tab_export.prioritizer import PrioritizingResult


@pytest.fixture()
def sample_export() -> TabExport:
    tabs = [
        Tab(title="GitHub Repo", url="https://github.com/user/repo", group="Dev"),
        Tab(title="BBC News", url="https://bbc.co.uk/news", group="News"),
    ]
    return TabExport(tabs=tabs, source_file="test.txt")


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"priority_rules": [], "show_top_n": 0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_prioritizer_args_registers_prioritize():
    parser = argparse.ArgumentParser()
    add_prioritizer_args(parser)
    actions = {a.dest for a in parser._actions}
    assert "priority_rules" in actions


def test_add_prioritizer_args_registers_show_top():
    parser = argparse.ArgumentParser()
    add_prioritizer_args(parser)
    actions = {a.dest for a in parser._actions}
    assert "show_top_n" in actions


def test_parse_priority_rules_returns_correct_count():
    rules = _parse_priority_rules(["url:github.com:10", "title:docs:8"])
    assert len(rules) == 2


def test_parse_priority_rules_sets_priority():
    rules = _parse_priority_rules(["url:github.com:10"])
    assert rules[0].priority == 10


def test_parse_priority_rules_invalid_raises():
    with pytest.raises(ValueError):
        _parse_priority_rules(["bad_format"])


def test_parse_priority_rules_bad_field_raises():
    with pytest.raises(ValueError):
        _parse_priority_rules(["domain:github:5"])


def test_apply_prioritizing_returns_result(sample_export):
    args = _make_args(priority_rules=["url:github.com:10"])
    result = apply_prioritizing(sample_export, args)
    assert isinstance(result, PrioritizingResult)


def test_apply_prioritizing_no_rules_zero_prioritized(sample_export):
    args = _make_args()
    result = apply_prioritizing(sample_export, args)
    assert result.total_prioritized == 0


def test_render_priority_summary_contains_header(sample_export):
    args = _make_args(priority_rules=["url:github.com:10"])
    result = apply_prioritizing(sample_export, args)
    summary = render_priority_summary(result)
    assert "Priority Summary" in summary


def test_render_priority_summary_top_n_lists_tabs(sample_export):
    args = _make_args(priority_rules=["url:github.com:10"])
    result = apply_prioritizing(sample_export, args)
    summary = render_priority_summary(result, top_n=1)
    assert "GitHub Repo" in summary


def test_render_priority_summary_ends_with_newline(sample_export):
    args = _make_args()
    result = apply_prioritizing(sample_export, args)
    assert render_priority_summary(result).endswith("\n")
