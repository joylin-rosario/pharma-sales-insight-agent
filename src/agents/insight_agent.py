"""Insight Agent (CLAUDE.md section 14).

Translates verified metrics into concise business insights, separating
facts from hypotheses and including limitations.
"""
from __future__ import annotations

from typing import Any

from src.analytics.kpi import KPIResult
from src.skills import generate_executive_summary


def run(summary: dict[str, KPIResult], scope_label: str, period: str | None = None) -> dict[str, list[str]]:
    return generate_executive_summary.run(summary, scope_label, period)
