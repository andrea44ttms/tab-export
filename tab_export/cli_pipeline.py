"""CLI argument helpers for constructing PipelineOptions from parsed args."""

import argparse
from typing import Optional

from tab_export.filter import FilterOptions
from tab_export.sorter import SortOptions, SortKey, SortOrder
from tab_export.exporter import PipelineOptions


def add_pipeline_args(parser: argparse.ArgumentParser) -> None:
    """Attach pipeline-related arguments to an ArgumentParser."""
    parser.add_argument(
        "--keyword",
        metavar="TERM",
        help="Filter tabs to those matching TERM in title or URL",
    )
    parser.add_argument(
        "--domain",
        metavar="DOMAIN",
        help="Filter tabs to those matching DOMAIN",
    )
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        default=False,
        help="Remove duplicate tabs (same URL) before output",
    )
    parser.add_argument(
        "--sort",
        choices=[k.value for k in SortKey],
        default=None,
        help="Sort tabs by this field",
    )
    parser.add_argument(
        "--sort-order",
        choices=[o.value for o in SortOrder],
        default="asc",
        dest="sort_order",
        help="Sort direction (default: asc)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Append a stats summary after the formatted output",
    )


def build_pipeline_options(args: argparse.Namespace, fmt: str) -> PipelineOptions:
    """Construct a PipelineOptions instance from parsed CLI args."""
    filter_opts: Optional[FilterOptions] = None
    if args.keyword or args.domain:
        filter_opts = FilterOptions(
            keyword=args.keyword or None,
            domain=args.domain or None,
        )

    sort_opts: Optional[SortOptions] = None
    if args.sort:
        sort_opts = SortOptions(
            key=SortKey(args.sort),
            order=SortOrder(args.sort_order),
        )

    return PipelineOptions(
        filter_opts=filter_opts,
        sort_opts=sort_opts,
        deduplicate=args.deduplicate,
        output_format=fmt,
        include_stats=args.stats,
    )
