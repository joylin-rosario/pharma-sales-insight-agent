"""Skill: analyze-business-unit. See .claude/skills/analyze-business-unit/SKILL.md."""
from __future__ import annotations

from typing import Any

import pandas as pd

from src.analytics.kpi import KPIResult, compute_contribution_breakdown, compute_summary


def run(df: pd.DataFrame, business_unit: str | None = None) -> dict[str, Any]:
    scoped = df if not business_unit else df[df["business_unit"] == business_unit]
    filters = {"business_unit": business_unit} if business_unit else {}
    summary = compute_summary(scoped, filters)
    area_contribution: list[KPIResult] = compute_contribution_breakdown(scoped, "area", filters)
    return {"summary": summary, "area_contribution": area_contribution}
