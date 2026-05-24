"""Statistics and summary reporting for tab exports."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from urllib.parse import urlparse

from tab_export.parser import TabExport


@dataclass
class ExportStats:
    total_tabs: int
    total_groups: int
    tabs_per_group: dict[str, int] = field(default_factory=dict)
    top_domains: list[tuple[str, int]] = field(default_factory=list)
    empty_groups: list[str] = field(default_factory=list)

    @property
    def avg_tabs_per_group(self) -> float:
        if self.total_groups == 0:
            return 0.0
        return round(self.total_tabs / self.total_groups, 2)

    def summary_lines(self) -> list[str]:
        lines = [
            f"Total tabs   : {self.total_tabs}",
            f"Total groups : {self.total_groups}",
            f"Avg per group: {self.avg_tabs_per_group}",
        ]
        if self.empty_groups:
            lines.append(f"Empty groups : {', '.join(self.empty_groups)}")
        if self.top_domains:
            lines.append("Top domains  :")
            for domain, count in self.top_domains:
                lines.append(f"  {domain}: {count}")
        return lines


def _extract_domain(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return host.removeprefix("www.")
    except Exception:
        return ""


def compute_stats(export: TabExport, top_n: int = 5) -> ExportStats:
    """Compute statistics from a TabExport."""
    tabs_per_group: dict[str, int] = {}
    empty_groups: list[str] = []
    domain_counter: Counter[str] = Counter()

    for group in export.groups():
        tabs = export.tabs_in_group(group)
        tabs_per_group[group] = len(tabs)
        if len(tabs) == 0:
            empty_groups.append(group)
        for tab in tabs:
            domain = _extract_domain(tab.url)
            if domain:
                domain_counter[domain] += 1

    return ExportStats(
        total_tabs=len(export.tabs),
        total_groups=len(export.groups()),
        tabs_per_group=tabs_per_group,
        top_domains=domain_counter.most_common(top_n),
        empty_groups=empty_groups,
    )
