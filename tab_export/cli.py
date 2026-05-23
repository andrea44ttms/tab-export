"""Command-line interface for tab-export."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tab_export.deduplicator import deduplicate
from tab_export.formatter import format_export
from tab_export.parser import parse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tab-export",
        description="Convert exported browser tab lists to Markdown or Notion format.",
    )
    p.add_argument("file", type=Path, help="Path to the exported tab list file.")
    p.add_argument(
        "--format",
        choices=["markdown", "notion"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    p.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write output to this file instead of stdout.",
    )
    p.add_argument(
        "--dedupe",
        action="store_true",
        default=False,
        help="Remove duplicate URLs before formatting.",
    )
    p.add_argument(
        "--dedupe-within-group",
        action="store_true",
        default=False,
        help="Remove duplicates only within each group (implies --dedupe).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1

    try:
        export = parse(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse file: {exc}", file=sys.stderr)
        return 1

    if args.dedupe or args.dedupe_within_group:
        across = not args.dedupe_within_group
        result = deduplicate(export, across_groups=across)
        export = result.export
        if result.removed_count:
            print(
                f"info: removed {result.removed_count} duplicate(s)",
                file=sys.stderr,
            )

    output = format_export(export, fmt=args.format)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
