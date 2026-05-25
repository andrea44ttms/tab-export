"""Templater: render a TabExport using a user-defined Jinja2-style template string."""
from __future__ import annotations

from dataclasses import dataclass
from string import Template
from typing import List

from tab_export.parser import TabExport


@dataclass
class TemplateResult:
    """Result of rendering a TabExport through a template."""

    rendered: str
    groups_rendered: int
    tabs_rendered: int

    @property
    def line_count(self) -> int:
        return len(self.rendered.splitlines())


# Default template uses Python stdlib string.Template syntax ($var / ${var}).
DEFAULT_GROUP_TEMPLATE = "## $group_name\n"
DEFAULT_TAB_TEMPLATE = "- [$title]($url)\n"


def _render_tab(tab_template: str, title: str, url: str, tags: str) -> str:
    """Substitute tab-level variables into the tab template."""
    t = Template(tab_template)
    return t.safe_substitute(title=title, url=url, tags=tags)


def _render_group(group_template: str, group_name: str) -> str:
    """Substitute group-level variables into the group template."""
    t = Template(group_template)
    return t.safe_substitute(group_name=group_name)


def render_template(
    export: TabExport,
    *,
    group_template: str = DEFAULT_GROUP_TEMPLATE,
    tab_template: str = DEFAULT_TAB_TEMPLATE,
    separator: str = "\n",
) -> TemplateResult:
    """Render *export* using the supplied templates.

    Variables available in *group_template*:
        $group_name  – name of the current group

    Variables available in *tab_template*:
        $title  – tab title
        $url    – tab URL
        $tags   – comma-separated tags (may be empty)
    """
    parts: List[str] = []
    groups_rendered = 0
    tabs_rendered = 0

    for group_name in export.groups:
        parts.append(_render_group(group_template, group_name))
        groups_rendered += 1

        for tab in export.tabs_in_group(group_name):
            tags_str = ", ".join(getattr(tab, "tags", []) or [])
            parts.append(_render_tab(tab_template, tab.title, tab.url, tags_str))
            tabs_rendered += 1

        parts.append(separator)

    rendered = "".join(parts)
    if not rendered.endswith("\n"):
        rendered += "\n"

    return TemplateResult(
        rendered=rendered,
        groups_rendered=groups_rendered,
        tabs_rendered=tabs_rendered,
    )
