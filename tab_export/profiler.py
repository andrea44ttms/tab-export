"""Profile a TabExport to identify browsing patterns and time-based insights."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from urllib.parse import urlparse
from typing import List, Dict

from tab_export.parser import TabExport, Tab


@dataclass
class ProfileResult:
    """Result of profiling a TabExport."""
    total_tabs: int
    total_groups: int
    top_domains: List[tuple]  # (domain, count)
    group_sizes: Dict[str, int]
    largest_group: str
    smallest_group: str
    unique_domains: int
    solo_domain_tabs: int  # tabs whose domain appears only once

    @property
    def summary_lines(self) -> List[str]:
        lines = [
            f"Total tabs: {self.total_tabs}",
            f"Total groups: {self.total_groups}",
            f"Unique domains: {self.unique_domains}",
            f"Largest group: {self.largest_group} ({self.group_sizes.get(self.largest_group, 0)} tabs)",
            f"Smallest group: {self.smallest_group} ({self.group_sizes.get(self.smallest_group, 0)} tabs)",
            "Top domains:",
        ]
        for domain, count in self.top_domains:
            lines.append(f"  {domain}: {count}")
        return lines


def _extract_domain(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return host.lstrip("www.")
    except Exception:
        return ""


def profile_export(export: TabExport, top_n: int = 5) -> ProfileResult:
    """Analyse a TabExport and return a ProfileResult."""
    all_tabs: List[Tab] = []
    group_sizes: Dict[str, int] = {}

    for group in export.groups():
        tabs = export.tabs_in_group(group)
        group_sizes[group] = len(tabs)
        all_tabs.extend(tabs)

    domain_counter: Counter = Counter(_extract_domain(t.url) for t in all_tabs)
    top_domains = domain_counter.most_common(top_n)
    solo_domain_tabs = sum(1 for t in all_tabs if domain_counter[_extract_domain(t.url)] == 1)

    sorted_groups = sorted(group_sizes.items(), key=lambda kv: kv[1])
    smallest_group = sorted_groups[0][0] if sorted_groups else ""
    largest_group = sorted_groups[-1][0] if sorted_groups else ""

    return ProfileResult(
        total_tabs=len(all_tabs),
        total_groups=len(group_sizes),
        top_domains=top_domains,
        group_sizes=group_sizes,
        largest_group=largest_group,
        smallest_group=smallest_group,
        unique_domains=len(domain_counter),
        solo_domain_tabs=solo_domain_tabs,
    )
