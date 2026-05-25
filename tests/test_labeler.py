"""Tests for tab_export.labeler."""
import pytest

from tab_export.labeler import LabelRule, LabelingResult, label_export
from tab_export.parser import Tab, TabExport


@pytest.fixture
def sample_export():
    tabs = [
        Tab(title="GitHub Repo", url="https://github.com/org/repo"),
        Tab(title="Python Docs", url="https://docs.python.org/3/"),
        Tab(title="Stack Overflow Answer", url="https://stackoverflow.com/a/12345"),
        Tab(title="My Notes", url="https://notion.so/my-notes"),
    ]
    return TabExport(groups_dict={"Work": tabs[:2], "Research": tabs[2:]}, source_file="test.txt")


@pytest.fixture
def rules():
    return [
        LabelRule(label="code", url_contains="github.com"),
        LabelRule(label="docs", title_contains="docs"),
        LabelRule(label="qa", url_contains="stackoverflow.com"),
        LabelRule(label="notes", keyword="notion"),
    ]


def test_label_export_returns_labeling_result(sample_export, rules):
    result = label_export(sample_export, rules)
    assert isinstance(result, LabelingResult)


def test_no_rules_labels_nothing(sample_export):
    result = label_export(sample_export, [])
    assert result.total_labeled == 0
    assert result.label_map == {}


def test_url_contains_rule_matches(sample_export, rules):
    result = label_export(sample_export, rules)
    github_tab = sample_export.groups_dict["Work"][0]
    assert "code" in result.labels_for(github_tab)


def test_title_contains_rule_matches(sample_export, rules):
    result = label_export(sample_export, rules)
    docs_tab = sample_export.groups_dict["Work"][1]
    assert "docs" in result.labels_for(docs_tab)


def test_keyword_rule_matches_url(sample_export, rules):
    result = label_export(sample_export, rules)
    notion_tab = sample_export.groups_dict["Research"][1]
    assert "notes" in result.labels_for(notion_tab)


def test_tab_can_have_multiple_labels():
    tab = Tab(title="GitHub Docs", url="https://github.com/docs")
    export = TabExport(groups_dict={"Dev": [tab]}, source_file="t.txt")
    rules = [
        LabelRule(label="code", url_contains="github.com"),
        LabelRule(label="docs", title_contains="docs"),
    ]
    result = label_export(export, rules)
    labels = result.labels_for(tab)
    assert "code" in labels
    assert "docs" in labels


def test_total_labeled_counts_tabs_with_any_label(sample_export, rules):
    result = label_export(sample_export, rules)
    assert result.total_labeled == 4


def test_labels_for_unlabeled_tab_returns_empty(sample_export):
    result = label_export(sample_export, [])
    tab = sample_export.groups_dict["Work"][0]
    assert result.labels_for(tab) == []


def test_duplicate_labels_not_added():
    tab = Tab(title="GitHub", url="https://github.com/x")
    export = TabExport(groups_dict={"G": [tab]}, source_file="t.txt")
    rules = [
        LabelRule(label="code", url_contains="github"),
        LabelRule(label="code", title_contains="github"),
    ]
    result = label_export(export, rules)
    assert result.labels_for(tab).count("code") == 1
