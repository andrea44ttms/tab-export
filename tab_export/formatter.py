"""Formatters for converting TabExport data into various output formats."""

from __future__ import annotations

from typing import Literal

from tab_export.parser import TabExport

OutputFormat = Literal["markdown", "notion"]


def format_markdown(export: TabExport) -> str:
    """Render a TabExport as a Markdown document.

    Each group becomes an H2 heading, and each tab becomes a bullet
    list item with a hyperlink.
    """
    lines: list[str] = []

    for group_name in export.groups:
        lines.append(f"## {group_name}\n")
        for tab in export.tabs_in_group(group_name):
            title = tab.title or tab.url
            lines.append(f"- [{title}]({tab.url})")
        lines.append("")  # blank line between groups

    return "\n".join(lines).rstrip() + "\n"


def format_notion(export: TabExport) -> str:
    """Render a TabExport as a Notion-ready Markdown document.

    Uses Notion-compatible syntax: H3 headings for groups and
    indented bookmark-style links as plain bullet items.
    """
    lines: list[str] = []

    for group_name in export.groups:
        lines.append(f"### {group_name}")
        lines.append("")
        for tab in export.tabs_in_group(group_name):
            title = tab.title or tab.url
            lines.append(f"- [{title}]({tab.url})")
        lines.append("")  # blank line between groups

    return "\n".join(lines).rstrip() + "\n"


def format_export(export: TabExport, fmt: OutputFormat = "markdown") -> str:
    """Dispatch to the correct formatter based on *fmt*."""
    if fmt == "markdown":
        return format_markdown(export)
    if fmt == "notion":
        return format_notion(export)
    raise ValueError(f"Unknown format: {fmt!r}")
