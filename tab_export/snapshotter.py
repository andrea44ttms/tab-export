"""Snapshot diffing: compare current export against a saved baseline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from tab_export.parser import Tab, TabExport
from tab_export.comparator import compare_exports, ComparisonResult


@dataclass
class SnapshotEntry:
    label: str
    export: TabExport


@dataclass
class SnapshotSession:
    baseline: Optional[SnapshotEntry] = None
    snapshots: List[SnapshotEntry] = field(default_factory=list)

    def add(self, label: str, export: TabExport) -> None:
        """Add a named snapshot to the session."""
        self.snapshots.append(SnapshotEntry(label=label, export=export))

    def set_baseline(self, label: str, export: TabExport) -> None:
        self.baseline = SnapshotEntry(label=label, export=export)


@dataclass
class SessionDiffResult:
    session: SnapshotSession
    diffs: List[ComparisonResult] = field(default_factory=list)

    @property
    def total_snapshots(self) -> int:
        return len(self.session.snapshots)

    @property
    def any_changes(self) -> bool:
        return any(not d.is_unchanged for d in self.diffs)


def diff_session(session: SnapshotSession) -> SessionDiffResult:
    """Diff each snapshot against the baseline (or previous snapshot)."""
    result = SessionDiffResult(session=session)
    snapshots = session.snapshots
    if not snapshots:
        return result

    entries = snapshots
    for i, entry in enumerate(entries):
        if session.baseline is not None:
            before = session.baseline.export
        elif i == 0:
            result.diffs.append(compare_exports(entry.export, entry.export))
            continue
        else:
            before = entries[i - 1].export
        result.diffs.append(compare_exports(before, entry.export))
    return result
