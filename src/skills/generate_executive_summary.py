"""Skill: generate-executive-summary. See .claude/skills/generate-executive-summary/SKILL.md.

Deterministic template-based narrative from verified KPIResults only — no
free-form LLM generation of numbers (CLAUDE.md sections 9-10).
"""
from __future__ import annotations

from typing import Any

from src.analytics.kpi import KPIResult


def run(summary: dict[str, KPIResult], scope_label: str, period: str | None) -> dict[str, list[str]]:
    facts: list[str] = []
    observations: list[str] = []
    hypotheses: list[str] = []
    recommendations: list[str] = []
    limitations: list[str] = []

    actual = summary["actual_sales"]
    target = summary["target_sales"]
    ach = summary["achievement_pct"]
    var = summary["variance_to_target"]
    growth = summary["growth_pct"]

    period_label = f" for {period}" if period else ""
    facts.append(f"{scope_label} Actual Sales{period_label}: {actual.display} (evidence: {actual.metric}).")
    facts.append(f"{scope_label} Target Sales{period_label}: {target.display} (evidence: {target.metric}).")

    if ach.value is not None:
        facts.append(f"{scope_label} Achievement %{period_label}: {ach.display} (evidence: {ach.metric}).")
        if ach.value >= 100:
            observations.append(f"{scope_label} met or exceeded target ({ach.display}).")
        else:
            observations.append(f"{scope_label} is below target by {var.display} ({ach.display} achievement).")
            hypotheses.append(
                "[HYPOTHESIS - requires human validation] The shortfall may relate to territory-level "
                "execution gaps or demand shifts; root cause is not determined by this data alone."
            )
            recommendations.append(
                "[RECOMMENDATION - subject to approval] Review the lowest-contributing territories "
                "for this scope and validate with the responsible manager before any action."
            )
    else:
        limitations.append(ach.reason or "Achievement % unavailable.")

    if growth.value is not None:
        facts.append(f"{scope_label} Growth %{period_label}: {growth.display} (evidence: {growth.metric}).")
    else:
        limitations.append(growth.reason or "Growth % unavailable.")

    limitations.append("This is a descriptive analytics summary; it does not establish causation.")

    return {
        "facts": facts,
        "observations": observations,
        "hypotheses": hypotheses,
        "recommendations": recommendations,
        "limitations": limitations,
    }
