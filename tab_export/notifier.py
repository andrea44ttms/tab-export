"""Notifier: attach human-readable notification messages to a pipeline run."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from tab_export.exporter import PipelineResult


@dataclass
class NotificationResult:
    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        lines: List[str] = []
        for msg in self.messages:
            lines.append(f"[info]  {msg}")
        for warn in self.warnings:
            lines.append(f"[warn]  {warn}")
        return "\n".join(lines)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def notify(result: PipelineResult, *, warn_threshold: int = 0) -> NotificationResult:
    """Build human-readable notifications from a PipelineResult.

    Args:
        result: The completed pipeline result.
        warn_threshold: Emit a warning when tabs_removed exceeds this value.
            Defaults to 0 (warn on any removal).
    """
    messages: List[str] = []
    warnings: List[str] = []

    messages.append(f"Processed {result.tabs_before} tab(s).")

    if result.dedup_removed:
        messages.append(
            f"Removed {result.dedup_removed} duplicate(s) during deduplication."
        )

    if result.filter_removed:
        messages.append(
            f"Filtered out {result.filter_removed} tab(s) by active filter rules."
        )

    if result.tabs_after == 0:
        warnings.append("No tabs remain after processing — output will be empty.")
    elif result.tabs_removed > warn_threshold:
        warnings.append(
            f"{result.tabs_removed} tab(s) were removed in total "
            f"({result.tabs_before} → {result.tabs_after})."
        )

    messages.append(f"Output contains {result.tabs_after} tab(s).")

    return NotificationResult(messages=messages, warnings=warnings)
