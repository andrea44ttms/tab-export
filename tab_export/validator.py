"""Validates tab exports for common issues such as broken URLs, empty titles, and malformed data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from tab_export.parser import Tab, TabExport


@dataclass
class ValidationIssue:
    group: str
    tab_url: str
    tab_title: str
    message: str

    def __str__(self) -> str:
        return f"[{self.group}] '{self.tab_title}' ({self.tab_url}): {self.message}"


@dataclass
class ValidationResult:
    export: TabExport
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def summary_lines(self) -> List[str]:
        if self.is_valid:
            return ["No validation issues found."]
        lines = [f"{self.issue_count} issue(s) found:"]
        for issue in self.issues:
            lines.append(f"  - {issue}")
        return lines


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def _validate_tab(tab: Tab, group: str) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not tab.title or not tab.title.strip():
        issues.append(ValidationIssue(group, tab.url, tab.title, "Empty or blank title"))
    if not tab.url or not tab.url.strip():
        issues.append(ValidationIssue(group, tab.url, tab.title, "Empty or blank URL"))
    elif not _is_valid_url(tab.url):
        issues.append(ValidationIssue(group, tab.url, tab.title, f"Invalid URL scheme or format"))
    return issues


def validate_export(export: TabExport) -> ValidationResult:
    """Validate all tabs in a TabExport and return a ValidationResult."""
    issues: List[ValidationIssue] = []
    for group in export.groups():
        for tab in export.tabs_in_group(group):
            issues.extend(_validate_tab(tab, group))
    return ValidationResult(export=export, issues=issues)
