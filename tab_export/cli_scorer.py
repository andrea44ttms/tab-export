"""CLI helpers for the tab scoring feature."""
from __future__ import annotations

import argparse
from typing import Dict, List

from tab_export.scorer import ScoringResult, score_export
from tab_export.parser import TabExport


def add_scorer_args(parser: argparse.ArgumentParser) -> None:
    """Register scoring-related CLI arguments onto *parser*."""
    parser.add_argument(
        "--score",
        metavar="KEYWORD:WEIGHT",
        action="append",
        default=[],
        dest="score_weights",
        help=(
            "Keyword weight pair used to score tabs, e.g. '--score github:2.0'. "
            "May be repeated.  Negative weights penalise matches."
        ),
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Exclude tabs whose score is below this threshold (requires --score).",
    )
    parser.add_argument(
        "--show-scores",
        action="store_true",
        default=False,
        help="Print a ranked score summary to stderr before main output.",
    )


def _parse_weights(raw: List[str]) -> Dict[str, float]:
    """Parse a list of 'keyword:weight' strings into a dict."""
    weights: Dict[str, float] = {}
    for item in raw:
        if ":" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid score weight '{item}': expected KEYWORD:WEIGHT"
            )
        keyword, _, raw_weight = item.partition(":")
        try:
            weights[keyword.strip()] = float(raw_weight.strip())
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid weight value in '{item}': must be a number"
            )
    return weights


def apply_scoring(
    export: TabExport,
    args: argparse.Namespace,
) -> TabExport:
    """Apply scoring pipeline step if --score flags are present.

    Returns the (possibly filtered) export.  If *--show-scores* is set,
    a ranked summary is printed to stderr.
    """
    if not args.score_weights:
        return export

    weights = _parse_weights(args.score_weights)
    result: ScoringResult = score_export(export, weights)

    if args.show_scores:
        import sys
        print("Tab scores (ranked):", file=sys.stderr)
        for st in result.top_tabs:
            print(f"  [{st.score:+.2f}] {st.title}  {st.url}", file=sys.stderr)

    if args.min_score is not None:
        return result.as_export(min_score=args.min_score)

    return export
