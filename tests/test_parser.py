"""Tests for the tab_export.parser module."""

import json
import pytest
from pathlib import Path

from tab_export.parser import Tab, TabExport, parse_json_export


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_export(tmp_path: Path) -> Path:
    data = [
        {"title": "GitHub", "url": "https://github.com", "group": "Dev"},
        {"title": "PyPI", "url": "https://pypi.org", "group": "Dev"},
        {"title": "BBC News", "url": "https://bbc.com/news", "group": "News"},
        {"url": "https://example.com"},  # no title, no group
    ]
    export_file = tmp_path / "tabs.json"
    export_file.write_text(json.dumps(data), encoding="utf-8")
    return export_file


# ---------------------------------------------------------------------------
# Tab dataclass
# ---------------------------------------------------------------------------

def test_tab_strips_whitespace():
    tab = Tab(title="  Hello  ", url="  https://example.com  ")
    assert tab.title == "Hello"
    assert tab.url == "https://example.com"


# ---------------------------------------------------------------------------
# parse_json_export
# ---------------------------------------------------------------------------

def test_parse_returns_tab_export(sample_export):
    result = parse_json_export(str(sample_export))
    assert isinstance(result, TabExport)
    assert len(result.tabs) == 4


def test_parse_sets_source_file(sample_export):
    result = parse_json_export(str(sample_export))
    assert result.source_file == str(sample_export)


def test_parse_tab_fields(sample_export):
    result = parse_json_export(str(sample_export))
    first = result.tabs[0]
    assert first.title == "GitHub"
    assert first.url == "https://github.com"
    assert first.group == "Dev"


def test_parse_missing_title_falls_back_to_url(sample_export):
    result = parse_json_export(str(sample_export))
    last = result.tabs[-1]
    assert last.title == "https://example.com"
    assert last.group is None


def test_parse_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_json_export("/nonexistent/path/tabs.json")


def test_parse_invalid_top_level(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps({"tabs": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        parse_json_export(str(bad_file))


def test_parse_missing_url_raises(tmp_path):
    bad_file = tmp_path / "no_url.json"
    bad_file.write_text(json.dumps([{"title": "No URL"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="'url'"):
        parse_json_export(str(bad_file))


# ---------------------------------------------------------------------------
# TabExport helpers
# ---------------------------------------------------------------------------

def test_groups_order(sample_export):
    result = parse_json_export(str(sample_export))
    assert result.groups == ["Dev", "News", "Ungrouped"]


def test_tabs_in_group(sample_export):
    result = parse_json_export(str(sample_export))
    dev_tabs = result.tabs_in_group("Dev")
    assert len(dev_tabs) == 2
    assert all(t.group == "Dev" for t in dev_tabs)


def test_tabs_in_ungrouped(sample_export):
    result = parse_json_export(str(sample_export))
    ungrouped = result.tabs_in_group("Ungrouped")
    assert len(ungrouped) == 1
    assert ungrouped[0].url == "https://example.com"
