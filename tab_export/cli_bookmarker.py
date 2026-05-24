"""CLI helpers for bookmark classification."""
from __future__ import annotations

import argparse
from typing import List

from tab_export.bookmarker import BookmarkResult, classify_bookmarks
from tab_export.parser import TabExport


def add_bookmarker_args(parser: argparse.ArgumentParser) -> None:
    """Register bookmark-related CLI flags onto *parser*."""
    parser.add_argument(
        "--classify-bookmarks",
        action="store_true",
        default=False,
        help="Classify tabs into bookmark categories and print a summary.",
    )
    parser.add_argument(
        "--show-category",
        metavar="CATEGORY",
        default=None,
        help="Only show tabs that belong to the given bookmark category.",
    )


def render_bookmark_summary(result: BookmarkResult) -> str:
    """Return a human-readable summary of bookmark classifications."""
    lines: List[str] = [
        f"Bookmark classification — {result.total_classified} tab(s) classified",
        "",
    ]
    by_cat = result.by_category()
    for category, tabs in sorted(by_cat.items()):
        lines.append(f"  {category} ({len(tabs)}):")
        for tab in tabs:
            lines.append(f"    - {tab.title} <{tab.url}>")
    return "\n".join(lines)


def apply_bookmark_classification(
    args: argparse.Namespace, export: TabExport
) -> TabExport:
    """Run classification and optionally filter export to a single category."""
    if not args.classify_bookmarks and not args.show_category:
        return export

    result = classify_bookmarks(export)

    if args.classify_bookmarks:
        print(render_bookmark_summary(result))

    if args.show_category:
        category = args.show_category.lower()
        by_cat = result.by_category()
        filtered_tabs = by_cat.get(category, [])
        from tab_export.parser import Tab
        from dataclasses import replace
        return TabExport(tabs=list(filtered_tabs))

    return export
