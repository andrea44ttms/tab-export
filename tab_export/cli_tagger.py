"""CLI helpers for the --tag flag: argument registration and integration."""
from __future__ import annotations

import argparse
from typing import Optional

from tab_export.parser import TabExport
from tab_export.tagger import TaggingResult, tag_export


def add_tagger_args(parser: argparse.ArgumentParser) -> None:
    """Register tagging-related CLI arguments onto *parser*."""
    group = parser.add_argument_group("tagging")
    group.add_argument(
        "--tag",
        action="store_true",
        default=False,
        help="Infer and append tags to tab titles based on URL/title patterns.",
    )
    group.add_argument(
        "--tag-summary",
        action="store_true",
        default=False,
        help="Print a tag frequency summary to stderr after processing.",
    )


def apply_tagging(
    export: TabExport,
    args: argparse.Namespace,
    stderr_write=None,
) -> TabExport:
    """Apply tagging to *export* if requested by *args*.

    Returns the (possibly modified) export.  Writes a tag summary to
    *stderr_write* (a callable) when --tag-summary is set.
    """
    if not getattr(args, "tag", False):
        return export

    result: TaggingResult = tag_export(export)

    if getattr(args, "tag_summary", False) and stderr_write is not None:
        lines = ["Tag summary:"]
        if result.tag_counts:
            for tag, count in sorted(result.tag_counts.items(), key=lambda x: -x[1]):
                lines.append(f"  {tag}: {count}")
        else:
            lines.append("  (no tags inferred)")
        stderr_write("\n".join(lines) + "\n")

    return result.export
