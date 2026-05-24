"""CLI helpers for the archive subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path

from tab_export.archiver import archive_export, load_archive, ArchiveEntry
from tab_export.parser import TabExport


def add_archive_args(parser: argparse.ArgumentParser) -> None:
    """Register archive-related CLI arguments."""
    parser.add_argument(
        "--archive-dir",
        metavar="DIR",
        default=None,
        help="Directory to store/read the archive file (default: disabled).",
    )
    parser.add_argument(
        "--show-archive",
        action="store_true",
        default=False,
        help="Print archive history instead of processing input.",
    )


def maybe_archive(export: TabExport, args: argparse.Namespace) -> None:
    """Archive the export if --archive-dir is set."""
    if not getattr(args, "archive_dir", None):
        return
    archive_dir = Path(args.archive_dir)
    result = archive_export(export, archive_dir)
    print(
        f"[archive] Saved snapshot #{result.total_entries} "
        f"({result.entry.tab_count} tabs, {result.entry.group_count} groups) "
        f"→ {result.archive_path}",
        flush=True,
    )


def render_archive_history(archive_dir: Path) -> str:
    """Return a human-readable string of all archive entries."""
    entries = load_archive(archive_dir)
    if not entries:
        return "No archive entries found."

    lines = [f"Archive history ({len(entries)} entries):", ""]
    for i, entry in enumerate(entries, 1):
        src = entry.source_file or "<unknown>"
        lines.append(
            f"  {i:>3}. [{entry.timestamp}] "
            f"{entry.tab_count} tabs in {entry.group_count} groups "
            f"(source: {src})"
        )
    return "\n".join(lines)


def handle_show_archive(args: argparse.Namespace) -> bool:
    """If --show-archive is set, print history and return True (caller should exit)."""
    if not getattr(args, "show_archive", False):
        return False
    archive_dir = getattr(args, "archive_dir", None)
    if not archive_dir:
        print("Error: --archive-dir required with --show-archive.")
        return True
    print(render_archive_history(Path(archive_dir)))
    return True
