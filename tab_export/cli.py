"""CLI entry point for tab-export."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tab_export.deduplicator import deduplicate
from tab_export.formatter import format_export
from tab_export.parser import parse
from tab_export.sorter import SortKey, SortOptions, SortOrder, sort_export


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tab-export",
        description="Convert exported browser tab lists to Markdown or Notion format.",
    )
    p.add_argument("input", type=Path, help="Path to the exported tab file.")
    p.add_argument(
        "-o", "--output", type=Path, default=None, help="Write output to file."
    )
    p.add_argument(
        "-f",
        "--format",
        choices=["markdown", "notion"],
        default="markdown",
        dest="fmt",
        help="Output format (default: markdown).",
    )
    p.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicate URLs before formatting.",
    )
    p.add_argument(
        "--sort",
        choices=[k.value for k in SortKey],
        default=None,
        metavar="KEY",
        help="Sort tabs by: title, url, or group.",
    )
    p.add_argument(
        "--sort-order",
        choices=[o.value for o in SortOrder],
        default="asc",
        dest="sort_order",
        help="Sort direction (default: asc).",
    )
    p.add_argument(
        "--sort-groups",
        action="store_true",
        dest="sort_groups",
        help="Also sort group names alphabetically.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1

    export = parse(args.input)

    if args.dedupe:
        result = deduplicate(export)
        export = result.export
        if result.removed_count > 0:
            print(
                f"Removed {result.removed_count} duplicate(s).", file=sys.stderr
            )

    if args.sort:
        opts = SortOptions(
            key=SortKey(args.sort),
            order=SortOrder(args.sort_order),
            sort_groups=args.sort_groups,
        )
        export = sort_export(export, opts)

    output = format_export(export, args.fmt)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
