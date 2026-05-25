"""Assign color labels to tabs based on keyword rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from tab_export.parser import Tab, TabExport

ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
}

VALID_COLORS = set(ANSI_COLORS) - {"reset"}


@dataclass
class ColorRule:
    keyword: str
    color: str
    match_field: str = "title"  # "title" | "url" | "both"

    def matches(self, tab: Tab) -> bool:
        kw = self.keyword.lower()
        if self.match_field in ("title", "both"):
            if kw in tab.title.lower():
                return True
        if self.match_field in ("url", "both"):
            if kw in tab.url.lower():
                return True
        return False


@dataclass
class ColorizingResult:
    export: TabExport
    color_map: dict = field(default_factory=dict)  # tab url -> color label

    @property
    def total_colorized(self) -> int:
        return len(self.color_map)


def _first_matching_color(tab: Tab, rules: List[ColorRule]) -> Optional[str]:
    for rule in rules:
        if rule.color not in VALID_COLORS:
            continue
        if rule.matches(tab):
            return rule.color
    return None


def colorize_export(
    export: TabExport,
    rules: List[ColorRule],
) -> ColorizingResult:
    """Apply color labels to tabs matching the given rules."""
    color_map: dict = {}
    for group_name, tabs in export.groups():
        for tab in tabs:
            color = _first_matching_color(tab, rules)
            if color is not None:
                color_map[tab.url] = color
    return ColorizingResult(export=export, color_map=color_map)


def render_colorized_text(result: ColorizingResult) -> str:
    """Render tabs with ANSI color labels applied to matching entries."""
    lines: List[str] = []
    for group_name, tabs in result.export.groups():
        lines.append(f"## {group_name}")
        for tab in tabs:
            color = result.color_map.get(tab.url)
            if color:
                prefix = ANSI_COLORS[color]
                suffix = ANSI_COLORS["reset"]
                lines.append(f"{prefix}- [{tab.title}]({tab.url}){suffix}")
            else:
                lines.append(f"- [{tab.title}]({tab.url})")
        lines.append("")
    return "\n".join(lines)
