"""Parser module for reading exported browser tab lists."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Tab:
    """Represents a single browser tab."""
    title: str
    url: str
    group: Optional[str] = None

    def __post_init__(self):
        self.title = self.title.strip()
        self.url = self.url.strip()


@dataclass
class TabExport:
    """Represents a full export of browser tabs."""
    tabs: List[Tab] = field(default_factory=list)
    source_file: Optional[str] = None

    @property
    def groups(self) -> List[str]:
        """Return unique group names, preserving order."""
        seen = []
        for tab in self.tabs:
            g = tab.group or "Ungrouped"
            if g not in seen:
                seen.append(g)
        return seen

    def tabs_in_group(self, group: str) -> List[Tab]:
        target = None if group == "Ungrouped" else group
        return [t for t in self.tabs if (t.group or None) == target]


def parse_json_export(path: str) -> TabExport:
    """Parse a JSON file exported by the browser extension.

    Expected format:
    [
      {"title": "...", "url": "...", "group": "..."},
      ...
    ]
    The "group" field is optional.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Export file not found: {path}")

    with file_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, list):
        raise ValueError("Expected a JSON array at the top level.")

    tabs = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {i} is not an object.")
        if "url" not in item:
            raise ValueError(f"Item at index {i} is missing required field 'url'.")
        tabs.append(Tab(
            title=item.get("title", item["url"]),
            url=item["url"],
            group=item.get("group"),
        ))

    return TabExport(tabs=tabs, source_file=str(file_path))
