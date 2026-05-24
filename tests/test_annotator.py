"""Tests for tab_export.annotator."""

import pytest

from tab_export.annotator import AnnotationRule, AnnotationResult, annotate_export
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        source_file="test.txt",
        raw_groups={
            "Work": [
                Tab(title="GitHub Repo", url="https://github.com/org/repo"),
                Tab(title="CI Dashboard", url="https://ci.example.com/builds"),
            ],
            "Reading": [
                Tab(title="Python Docs", url="https://docs.python.org/3/"),
            ],
        },
    )


def test_annotate_returns_annotation_result(sample_export):
    result = annotate_export(sample_export, rules=[])
    assert isinstance(result, AnnotationResult)


def test_no_rules_produces_no_annotations(sample_export):
    result = annotate_export(sample_export, rules=[])
    assert result.total_annotated == 0
    assert result.annotations == {}


def test_url_contains_rule_matches(sample_export):
    rules = [AnnotationRule(note="Version control", url_contains="github.com")]
    result = annotate_export(sample_export, rules=rules)
    assert "https://github.com/org/repo" in result.annotations
    assert result.annotations["https://github.com/org/repo"] == "Version control"


def test_title_contains_rule_matches(sample_export):
    rules = [AnnotationRule(note="Documentation", title_contains="docs")]
    result = annotate_export(sample_export, rules=rules)
    assert "https://docs.python.org/3/" in result.annotations


def test_combined_url_and_title_rule(sample_export):
    rules = [
        AnnotationRule(
            note="CI system", url_contains="ci.example.com", title_contains="CI"
        )
    ]
    result = annotate_export(sample_export, rules=rules)
    assert "https://ci.example.com/builds" in result.annotations


def test_combined_rule_requires_both_conditions(sample_export):
    # url matches but title does not
    rules = [
        AnnotationRule(
            note="Should not match",
            url_contains="github.com",
            title_contains="nonexistent",
        )
    ]
    result = annotate_export(sample_export, rules=rules)
    assert "https://github.com/org/repo" not in result.annotations


def test_first_matching_rule_wins(sample_export):
    rules = [
        AnnotationRule(note="First", url_contains="github.com"),
        AnnotationRule(note="Second", url_contains="github.com"),
    ]
    result = annotate_export(sample_export, rules=rules)
    assert result.annotations["https://github.com/org/repo"] == "First"


def test_total_annotated_count(sample_export):
    rules = [
        AnnotationRule(note="Code", url_contains="github.com"),
        AnnotationRule(note="Docs", url_contains="docs.python.org"),
    ]
    result = annotate_export(sample_export, rules=rules)
    assert result.total_annotated == 2


def test_matching_is_case_insensitive(sample_export):
    rules = [AnnotationRule(note="Repo", url_contains="GITHUB.COM")]
    result = annotate_export(sample_export, rules=rules)
    assert "https://github.com/org/repo" in result.annotations


def test_original_export_is_unchanged(sample_export):
    rules = [AnnotationRule(note="x", url_contains="github.com")]
    annotate_export(sample_export, rules=rules)
    groups = dict(sample_export.groups())
    assert len(groups["Work"]) == 2
