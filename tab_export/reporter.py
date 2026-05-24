"""Render ExportStats as human-readable or markdown text."""
from __future__ import annotations

from tab_export.stats import ExportStats


def render_stats_text(stats: ExportStats) -> str:
    """Render stats as a plain-text report."""
    lines = ["=== Tab Export Statistics ==="]
    lines.extend(stats.summary_lines())
    lines.append("")
    lines.append("Tabs per group:")
    for group, count in sorted(stats.tabs_per_group.items()):
        bar = "#" * count
        lines.append(f"  {group:<20} {bar} ({count})")
    return "\n".join(lines) + "\n"


def render_stats_markdown(stats: ExportStats) -> str:
    """Render stats as a markdown report."""
    lines = ["## Tab Export Statistics", ""]
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total tabs | {stats.total_tabs} |")
    lines.append(f"| Total groups | {stats.total_groups} |")
    lines.append(f"| Avg tabs/group | {stats.avg_tabs_per_group} |")
    lines.append("")

    if stats.tabs_per_group:
        lines.append("### Tabs per Group")
        lines.append("")
        lines.append("| Group | Count |")
        lines.append("|-------|-------|")
        for group, count in sorted(stats.tabs_per_group.items()):
            lines.append(f"| {group} | {count} |")
        lines.append("")

    if stats.top_domains:
        lines.append("### Top Domains")
        lines.append("")
        lines.append("| Domain | Tabs |")
        lines.append("|--------|------|")
        for domain, count in stats.top_domains:
            lines.append(f"| {domain} | {count} |")
        lines.append("")

    if stats.empty_groups:
        lines.append(f"> **Empty groups:** {', '.join(stats.empty_groups)}")
        lines.append("")

    return "\n".join(lines)
