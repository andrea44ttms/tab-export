"""Integration tests for the prioritizer across multi-group exports."""
from __future__ import annotations

import pytest

from tab_export.parser import Tab, TabExport
from tab_export.prioritizer import PriorityRule, prioritize_export


def _make_export(groups: dict) -> TabExport:
    """Build a TabExport from {group_name: [(title, url), ...]}."""
    tabs = [
        Tab(title=title, url=url, group=group)
        for group, entries in groups.items()
        for title, url in entries
    ]
    return TabExport(tabs=tabs, source_file="integration.txt")


def test_priority_map_spans_multiple_groups():
    export = _make_export({
        "Dev": [("GitHub", "https://github.com"), ("PyPI", "https://pypi.org")],
        "News": [("BBC", "https://bbc.co.uk"), ("CNN", "https://cnn.com")],
    })
    rules = [PriorityRule(keyword="github", field="url", priority=10)]
    result = prioritize_export(export, rules)
    assert len(result.priority_map) == 4


def test_only_matching_tabs_get_nonzero_priority():
    export = _make_export({
        "Dev": [("GitHub", "https://github.com"), ("PyPI", "https://pypi.org")],
    })
    rules = [PriorityRule(keyword="github", field="url", priority=5)]
    result = prioritize_export(export, rules)
    assert result.total_prioritized == 1


def test_top_tabs_excludes_zero_priority_tabs():
    export = _make_export({
        "Dev": [("GitHub", "https://github.com"), ("PyPI", "https://pypi.org")],
        "News": [("BBC", "https://bbc.co.uk")],
    })
    rules = [PriorityRule(keyword="github", field="url", priority=7)]
    result = prioritize_export(export, rules)
    top = result.top_tabs(n=10)
    assert all(result.priority_for(t) > 0 for t in top)


def test_large_export_all_tabs_in_priority_map():
    groups = {f"Group{i}": [(f"Tab{j}", f"https://example.com/{i}/{j}") for j in range(5)] for i in range(6)}
    export = _make_export(groups)
    rules = [PriorityRule(keyword="example", field="url", priority=3)]
    result = prioritize_export(export, rules)
    expected = sum(len(v) for v in groups.values())
    assert len(result.priority_map) == expected
