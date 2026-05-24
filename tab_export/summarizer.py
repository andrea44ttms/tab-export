"""Summarizer: generate a plain-text or markdown summary of a TabExport."""

from dataclasses import dataclass
from typing import List

from tab_export.parser import TabExport
from tab_export.stats import compute_stats


@dataclass
class SummaryOptions:
    max_top_domains: int = 5
    include_group_breakdown: bool = True


@dataclass
class SummaryResult:
    lines: List[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def summarize_export(export: TabExport, options: SummaryOptions | None = None) -> SummaryResult:
    """Produce a human-readable summary of *export*."""
    if options is None:
        options = SummaryOptions()

    stats = compute_stats(export)
    lines: List[str] = []

    lines.append(f"Total tabs   : {stats.total_tabs}")
    lines.append(f"Total groups : {stats.total_groups}")

    avg = stats.avg_tabs_per_group
    lines.append(f"Avg per group: {avg:.1f}")

    if options.include_group_breakdown and stats.total_groups > 0:
        lines.append("")
        lines.append("Groups:")
        for group_name, tab_list in export.groups().items():
            lines.append(f"  {group_name} ({len(tab_list)} tab{'s' if len(tab_list) != 1 else ''})")

    if stats.top_domains:
        lines.append("")
        lines.append("Top domains:")
        for domain, count in stats.top_domains[: options.max_top_domains]:
            lines.append(f"  {domain}: {count}")

    return SummaryResult(lines=lines)


def summarize_export_markdown(export: TabExport, options: SummaryOptions | None = None) -> SummaryResult:
    """Produce a markdown-formatted summary of *export*."""
    if options is None:
        options = SummaryOptions()

    stats = compute_stats(export)
    lines: List[str] = []

    lines.append("## Export Summary")
    lines.append("")
    lines.append(f"- **Total tabs**: {stats.total_tabs}")
    lines.append(f"- **Total groups**: {stats.total_groups}")
    lines.append(f"- **Avg tabs per group**: {stats.avg_tabs_per_group:.1f}")

    if options.include_group_breakdown and stats.total_groups > 0:
        lines.append("")
        lines.append("### Groups")
        for group_name, tab_list in export.groups().items():
            lines.append(f"- **{group_name}**: {len(tab_list)} tab{'s' if len(tab_list) != 1 else ''}")

    if stats.top_domains:
        lines.append("")
        lines.append("### Top Domains")
        for domain, count in stats.top_domains[: options.max_top_domains]:
            lines.append(f"- `{domain}`: {count}")

    lines.append("")
    return SummaryResult(lines=lines)
