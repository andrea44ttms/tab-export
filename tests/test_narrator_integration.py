"""Integration tests for the narrator module."""
from __future__ import annotations

import pytest

from tab_export.parser import TabExport
from tab_export.narrator import narrate_export


def _make_export(groups: dict) -> TabExport:
    """Build a TabExport from a dict of {group_name: [(url, title), ...]}."""
    lines = []
    for name, tabs in groups.items():
        lines.append(f"Group: {name}")
        for url, title in tabs:
            lines.append(f"  - {url} | {title}")
    return TabExport.parse("\n".join(lines))


def test_large_export_text_is_nonempty():
    export = _make_export({
        "Alpha": [(f"https://a{i}.com", f"A{i}") for i in range(10)],
        "Beta": [(f"https://b{i}.com", f"B{i}") for i in range(5)],
        "Gamma": [(f"https://g{i}.com", f"G{i}") for i in range(3)],
    })
    result = narrate_export(export)
    assert len(result.text) > 0


def test_verbose_lists_every_group():
    groups = {"X": [("https://x.com", "X")], "Y": [("https://y.com", "Y")], "Z": [("https://z.com", "Z")]}
    export = _make_export(groups)
    result = narrate_export(export, verbose=True)
    for name in groups:
        assert name in result.text


def test_total_tab_count_matches_export():
    export = _make_export({
        "One": [("https://a.com", "A"), ("https://b.com", "B")],
        "Two": [("https://c.com", "C")],
    })
    result = narrate_export(export)
    assert "3" in result.text


def test_single_group_uses_singular():
    export = _make_export({"Only": [("https://only.com", "Only")]})
    result = narrate_export(export)
    assert "1 group" in result.text
    assert "groups" not in result.text
