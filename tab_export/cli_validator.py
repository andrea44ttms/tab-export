"""CLI helpers for the validator feature."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from tab_export.parser import TabExport
from tab_export.validator import ValidationResult, validate_export


def add_validator_args(parser: argparse.ArgumentParser) -> None:
    """Register --validate and --strict flags on an existing ArgumentParser."""
    parser.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="Run validation checks on the export and print any issues.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with a non-zero status code if validation issues are found (requires --validate).",
    )


def run_validation(
    export: TabExport,
    args: argparse.Namespace,
    out=None,
) -> Optional[ValidationResult]:
    """Run validation if requested and print results.  Returns the result or None."""
    if not getattr(args, "validate", False):
        return None

    if out is None:
        out = sys.stdout

    result = validate_export(export)
    for line in result.summary_lines():
        out.write(line + "\n")

    if getattr(args, "strict", False) and not result.is_valid:
        sys.exit(2)

    return result


def render_validation_report(result: ValidationResult) -> str:
    """Return a plain-text validation report string."""
    lines = ["## Validation Report"]
    lines += result.summary_lines()
    if not result.is_valid:
        lines.append("")
        lines.append(f"Total issues: {result.issue_count}")
    return "\n".join(lines)
