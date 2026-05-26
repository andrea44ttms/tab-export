"""Narrator: produce human-readable prose summaries of a TabExport."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from tab_export.parser import TabExport
from tab_export.stats import compute_stats


@dataclass
class NarrationResult:
    lines: List[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def narrate_export(export: TabExport, verbose: bool = False) -> NarrationResult:
    """Generate a prose narrative describing the export."""
    stats = compute_stats(export)
    lines: List[str] = []

    group_word = "group" if stats.total_groups == 1 else "groups"
    tab_word = "tab" if stats.total_tabs == 1 else "tabs"

    lines.append(
        f"This export contains {stats.total_tabs} {tab_word} "
        f"spread across {stats.total_groups} {group_word}."
    )

    if stats.total_groups > 0:
        avg = stats.avg_tabs_per_group
        lines.append(f"On average, each group holds {avg:.1f} tabs.")

    if stats.top_domains:
        top = stats.top_domains[0]
        lines.append(f"The most common domain is '{top}'.")

    if verbose and stats.total_groups > 0:
        lines.append("")
        lines.append("Group breakdown:")
        for group in export.groups():
            count = len(group.tabs)
            word = "tab" if count == 1 else "tabs"
            lines.append(f"  - {group.name}: {count} {word}")

    return NarrationResult(lines=lines)
