"""CLI helpers for the snapshotter feature."""
from __future__ import annotations

import argparse
from typing import List

from tab_export.parser import TabExport
from tab_export.snapshotter import SnapshotSession, SessionDiffResult, diff_session


def add_snapshotter_args(parser: argparse.ArgumentParser) -> None:
    """Register --snapshot and --baseline flags on *parser*."""
    parser.add_argument(
        "--snapshot",
        metavar="FILE",
        action="append",
        dest="snapshot_files",
        default=[],
        help="Additional export file to compare (may be repeated).",
    )
    parser.add_argument(
        "--baseline",
        metavar="FILE",
        dest="baseline_file",
        default=None,
        help="Treat this file as the fixed baseline for all diffs.",
    )
    parser.add_argument(
        "--show-diff",
        action="store_true",
        default=False,
        help="Print a per-snapshot diff summary.",
    )


def build_session(
    snapshots: List[TabExport],
    labels: List[str],
    baseline: TabExport | None = None,
    baseline_label: str = "baseline",
) -> SnapshotSession:
    session = SnapshotSession()
    if baseline is not None:
        session.set_baseline(baseline_label, baseline)
    for label, export in zip(labels, snapshots):
        session.add(label, export)
    return session


def render_session_summary(result: SessionDiffResult) -> str:
    lines: List[str] = ["## Snapshot Diff Summary", ""]
    for i, diff in enumerate(result.diffs):
        label = result.session.snapshots[i].label
        lines.append(f"### {label}")
        for line in diff.summary_lines():
            lines.append(f"  {line}")
        lines.append("")
    if not result.any_changes:
        lines.append("No changes detected across snapshots.")
    return "\n".join(lines)
