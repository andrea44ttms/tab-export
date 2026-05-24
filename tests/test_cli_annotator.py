"""Tests for tab_export.cli_annotator."""

import argparse
import json
import textwrap
from pathlib import Path

import pytest

from tab_export.annotator import AnnotationResult, annotate_export
from tab_export.cli_annotator import (
    add_annotator_args,
    load_rules,
    render_annotation_summary,
)
from tab_export.parser import Tab, TabExport


@pytest.fixture()
def rules_file(tmp_path: Path) -> Path:
    rules = [
        {"note": "Code host", "url_contains": "github.com"},
        {"note": "Docs", "title_contains": "docs"},
    ]
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(rules), encoding="utf-8")
    return p


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        source_file="t.txt",
        raw_groups={
            "Dev": [
                Tab(title="My Repo", url="https://github.com/me/repo"),
                Tab(title="Python Docs", url="https://docs.python.org"),
            ]
        },
    )


def test_add_annotator_args_registers_annotate():
    parser = argparse.ArgumentParser()
    add_annotator_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "annotate")
    assert args.annotate is None


def test_add_annotator_args_registers_show_annotations():
    parser = argparse.ArgumentParser()
    add_annotator_args(parser)
    args = parser.parse_args(["--show-annotations"])
    assert args.show_annotations is True


def test_load_rules_returns_correct_count(rules_file):
    rules = load_rules(str(rules_file))
    assert len(rules) == 2


def test_load_rules_url_contains(rules_file):
    rules = load_rules(str(rules_file))
    assert rules[0].url_contains == "github.com"
    assert rules[0].note == "Code host"


def test_load_rules_title_contains(rules_file):
    rules = load_rules(str(rules_file))
    assert rules[1].title_contains == "docs"
    assert rules[1].url_contains is None


def test_render_annotation_summary_header(sample_export):
    from tab_export.annotator import AnnotationRule

    rules = [AnnotationRule(note="Code host", url_contains="github.com")]
    result = annotate_export(sample_export, rules)
    summary = render_annotation_summary(result)
    assert "Annotations applied: 1" in summary


def test_render_annotation_summary_lists_urls(sample_export):
    from tab_export.annotator import AnnotationRule

    rules = [AnnotationRule(note="Code host", url_contains="github.com")]
    result = annotate_export(sample_export, rules)
    summary = render_annotation_summary(result)
    assert "https://github.com/me/repo" in summary


def test_render_annotation_summary_empty():
    export = TabExport(source_file="x.txt", raw_groups={})
    result = AnnotationResult(export=export)
    summary = render_annotation_summary(result)
    assert "Annotations applied: 0" in summary
