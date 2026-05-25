"""Tests for tab_export.validator."""
import pytest

from tab_export.parser import Tab, TabExport
from tab_export.validator import (
    ValidationIssue,
    ValidationResult,
    _is_valid_url,
    validate_export,
)


@pytest.fixture
def clean_export():
    return TabExport(
        tabs=[
            Tab(group="Work", title="GitHub", url="https://github.com"),
            Tab(group="Work", title="Docs", url="https://docs.python.org"),
            Tab(group="News", title="HN", url="https://news.ycombinator.com"),
        ],
        source_file="test.txt",
    )


@pytest.fixture
def dirty_export():
    return TabExport(
        tabs=[
            Tab(group="Work", title="", url="https://github.com"),
            Tab(group="Work", title="No Scheme", url="github.com"),
            Tab(group="Misc", title="FTP Tab", url="ftp://files.example.com"),
            Tab(group="Misc", title="Good Tab", url="https://example.com"),
            Tab(group="Empty", title="   ", url="https://example.org"),
        ],
        source_file="test.txt",
    )


def test_validate_returns_validation_result(clean_export):
    result = validate_export(clean_export)
    assert isinstance(result, ValidationResult)


def test_clean_export_is_valid(clean_export):
    result = validate_export(clean_export)
    assert result.is_valid


def test_clean_export_has_no_issues(clean_export):
    result = validate_export(clean_export)
    assert result.issue_count == 0


def test_empty_title_produces_issue(dirty_export):
    result = validate_export(dirty_export)
    messages = [i.message for i in result.issues]
    assert any("Empty or blank title" in m for m in messages)


def test_blank_title_produces_issue(dirty_export):
    result = validate_export(dirty_export)
    blank_issues = [i for i in result.issues if "   " == i.tab_title or not i.tab_title.strip()]
    assert len(blank_issues) >= 1


def test_invalid_url_scheme_produces_issue(dirty_export):
    result = validate_export(dirty_export)
    ftp_issues = [i for i in result.issues if "ftp://" in i.tab_url]
    assert len(ftp_issues) == 1
    assert "Invalid URL" in ftp_issues[0].message


def test_missing_scheme_produces_issue(dirty_export):
    result = validate_export(dirty_export)
    no_scheme = [i for i in result.issues if i.tab_url == "github.com"]
    assert len(no_scheme) == 1


def test_issue_count_matches_issues_list(dirty_export):
    result = validate_export(dirty_export)
    assert result.issue_count == len(result.issues)


def test_is_valid_false_when_issues_exist(dirty_export):
    result = validate_export(dirty_export)
    assert not result.is_valid


def test_summary_lines_no_issues(clean_export):
    result = validate_export(clean_export)
    lines = result.summary_lines()
    assert lines == ["No validation issues found."]


def test_summary_lines_with_issues(dirty_export):
    result = validate_export(dirty_export)
    lines = result.summary_lines()
    assert lines[0].startswith(str(result.issue_count))
    assert len(lines) > 1


def test_issue_str_contains_group_and_url():
    issue = ValidationIssue(group="Dev", tab_url="https://x.com", tab_title="X", message="test msg")
    s = str(issue)
    assert "Dev" in s
    assert "https://x.com" in s
    assert "test msg" in s


def test_is_valid_url_accepts_https():
    assert _is_valid_url("https://example.com") is True


def test_is_valid_url_rejects_ftp():
    assert _is_valid_url("ftp://example.com") is False


def test_is_valid_url_rejects_bare_domain():
    assert _is_valid_url("example.com") is False
