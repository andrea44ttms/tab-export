"""Tests for tab_export.renamer."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.renamer import RenameRule, RenamingResult, rename_export


@pytest.fixture
def sample_export():
    groups = {
        "Work": [
            Tab(url="https://github.com/org/repo", title="GitHub - org/repo", group="Work"),
            Tab(url="https://jira.example.com/browse/PROJ-1", title="PROJ-1 - Fix bug", group="Work"),
        ],
        "Reading": [
            Tab(url="https://example.com/article", title="Example Article - Example Site", group="Reading"),
        ],
    }
    return TabExport(source_file="test.txt", _groups=groups)


def test_rename_returns_renaming_result(sample_export):
    result = rename_export(sample_export, [])
    assert isinstance(result, RenamingResult)


def test_no_rules_leaves_titles_unchanged(sample_export):
    result = rename_export(sample_export, [])
    titles = [t.title for g in result.export.groups for t in result.export.tabs_in_group(g)]
    assert "GitHub - org/repo" in titles
    assert result.total_renamed == 0


def test_simple_replacement_renames_title(sample_export):
    rules = [RenameRule(pattern="GitHub - ", replacement="")]
    result = rename_export(sample_export, rules)
    titles = [t.title for t in result.export.tabs_in_group("Work")]
    assert "org/repo" in titles


def test_total_renamed_counts_changed_tabs(sample_export):
    rules = [RenameRule(pattern="- ", replacement="| ")]
    result = rename_export(sample_export, rules)
    assert result.total_renamed == 3


def test_case_insensitive_replacement(sample_export):
    rules = [RenameRule(pattern="github", replacement="GitLab", case_sensitive=False)]
    result = rename_export(sample_export, rules)
    titles = [t.title for t in result.export.tabs_in_group("Work")]
    assert any("GitLab" in t for t in titles)


def test_case_sensitive_no_match(sample_export):
    rules = [RenameRule(pattern="github", replacement="GitLab", case_sensitive=True)]
    result = rename_export(sample_export, rules)
    assert result.total_renamed == 0


def test_regex_rule_applies_pattern(sample_export):
    rules = [RenameRule(pattern=r"\s-\s.*$", replacement="", use_regex=True)]
    result = rename_export(sample_export, rules)
    titles = [t.title for t in result.export.tabs_in_group("Work")]
    assert "GitHub" in titles


def test_regex_rule_case_insensitive(sample_export):
    rules = [RenameRule(pattern=r"example", replacement="Demo", use_regex=True, case_sensitive=False)]
    result = rename_export(sample_export, rules)
    titles = [t.title for t in result.export.tabs_in_group("Reading")]
    assert any("Demo" in t for t in titles)


def test_groups_preserved_after_rename(sample_export):
    rules = [RenameRule(pattern="GitHub - ", replacement="")]
    result = rename_export(sample_export, rules)
    assert set(result.export.groups) == {"Work", "Reading"}


def test_url_unchanged_after_rename(sample_export):
    rules = [RenameRule(pattern="GitHub - ", replacement="")]
    result = rename_export(sample_export, rules)
    urls = [t.url for t in result.export.tabs_in_group("Work")]
    assert "https://github.com/org/repo" in urls


def test_multiple_rules_applied_in_order(sample_export):
    rules = [
        RenameRule(pattern="GitHub - ", replacement=""),
        RenameRule(pattern="org/", replacement=""),
    ]
    result = rename_export(sample_export, rules)
    titles = [t.title for t in result.export.tabs_in_group("Work")]
    assert "repo" in titles
