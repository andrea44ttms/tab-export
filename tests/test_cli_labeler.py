"""Tests for tab_export.cli_labeler."""
import argparse
import json
import textwrap
from pathlib import Path

import pytest

from tab_export.cli_labeler import (
    add_labeler_args,
    apply_labeling,
    load_label_rules,
    render_label_summary,
)
from tab_export.labeler import LabelingResult, label_export
from tab_export.parser import Tab, TabExport


@pytest.fixture
def sample_export():
    tabs = [
        Tab(title="GitHub", url="https://github.com/x"),
        Tab(title="Docs", url="https://docs.example.com"),
    ]
    return TabExport(groups_dict={"Dev": tabs}, source_file="t.txt")


@pytest.fixture
def rules_file(tmp_path):
    data = [
        {"label": "code", "url_contains": "github.com"},
        {"label": "docs", "title_contains": "docs"},
    ]
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def _make_args(**kwargs):
    ns = argparse.Namespace(label_rules=None, show_labels=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_labeler_args_registers_label_rules():
    parser = argparse.ArgumentParser()
    add_labeler_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "label_rules")


def test_add_labeler_args_registers_show_labels():
    parser = argparse.ArgumentParser()
    add_labeler_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "show_labels")


def test_load_label_rules_returns_correct_count(rules_file):
    rules = load_label_rules(rules_file)
    assert len(rules) == 2


def test_load_label_rules_sets_label(rules_file):
    rules = load_label_rules(rules_file)
    labels = [r.label for r in rules]
    assert "code" in labels
    assert "docs" in labels


def test_apply_labeling_returns_none_without_flag(sample_export):
    args = _make_args(label_rules=None)
    assert apply_labeling(sample_export, args) is None


def test_apply_labeling_returns_result_with_flag(sample_export, rules_file):
    args = _make_args(label_rules=rules_file)
    result = apply_labeling(sample_export, args)
    assert isinstance(result, LabelingResult)


def test_render_label_summary_contains_header(sample_export):
    from tab_export.labeler import LabelRule
    rules = [LabelRule(label="code", url_contains="github")]
    result = label_export(sample_export, rules)
    summary = render_label_summary(result)
    assert "Label Summary" in summary


def test_render_label_summary_contains_count(sample_export):
    from tab_export.labeler import LabelRule
    rules = [LabelRule(label="code", url_contains="github")]
    result = label_export(sample_export, rules)
    summary = render_label_summary(result)
    assert "1" in summary
