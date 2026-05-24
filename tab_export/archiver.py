"""Archive tab exports with timestamps for history tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from tab_export.parser import TabExport, Tab

ARCHIVE_FILENAME = "tab_archive.json"


@dataclass
class ArchiveEntry:
    timestamp: str
    source_file: Optional[str]
    group_count: int
    tab_count: int
    groups: dict  # {group_name: [{title, url}]}

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source_file": self.source_file,
            "group_count": self.group_count,
            "tab_count": self.tab_count,
            "groups": self.groups,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        return cls(
            timestamp=data["timestamp"],
            source_file=data.get("source_file"),
            group_count=data["group_count"],
            tab_count=data["tab_count"],
            groups=data["groups"],
        )


@dataclass
class ArchiveResult:
    entry: ArchiveEntry
    archive_path: Path
    total_entries: int


def _export_to_entry(export: TabExport) -> ArchiveEntry:
    groups: dict = {}
    for group in export.groups():
        tabs = export.tabs_in_group(group)
        groups[group] = [{"title": t.title, "url": t.url} for t in tabs]

    all_tabs = [t for g in export.groups() for t in export.tabs_in_group(g)]
    return ArchiveEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_file=str(export.source_file) if export.source_file else None,
        group_count=len(export.groups()),
        tab_count=len(all_tabs),
        groups=groups,
    )


def archive_export(export: TabExport, archive_dir: Path) -> ArchiveResult:
    """Append export snapshot to the archive file in archive_dir."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / ARCHIVE_FILENAME

    entries: List[dict] = []
    if archive_path.exists():
        entries = json.loads(archive_path.read_text(encoding="utf-8"))

    entry = _export_to_entry(export)
    entries.append(entry.to_dict())
    archive_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    return ArchiveResult(
        entry=entry,
        archive_path=archive_path,
        total_entries=len(entries),
    )


def load_archive(archive_dir: Path) -> List[ArchiveEntry]:
    """Load all archive entries from the archive directory."""
    archive_path = archive_dir / ARCHIVE_FILENAME
    if not archive_path.exists():
        return []
    data = json.loads(archive_path.read_text(encoding="utf-8"))
    return [ArchiveEntry.from_dict(d) for d in data]
