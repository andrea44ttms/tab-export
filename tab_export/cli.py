"""Command-line interface for tab-export."""

import argparse
import sys
from pathlib import Path

from tab_export.parser import parse
from tab_export.formatter import format_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tab-export",
        description="Convert exported browser tab lists into organized markdown or Notion-ready format.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the exported tab list file.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "notion"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write output to this file instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path: Path = args.input
    if not input_path.exists():
        print(f"error: file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        tab_export = parse(input_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to parse {input_path}: {exc}", file=sys.stderr)
        return 1

    output = format_export(tab_export, fmt=args.format)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
