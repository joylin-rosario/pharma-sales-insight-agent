"""Skill: calculate-sales-kpis. See .claude/skills/calculate-sales-kpis/SKILL.md."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from src.analytics.kpi import KPIResult, compute_summary


def run(df: pd.DataFrame, filters: dict[str, Any], period: Optional[str] = None) -> dict[str, KPIResult]:
    filtered = df.copy()
    for col, value in filters.items():
        if value and col in filtered.columns:
            filtered = filtered[filtered[col] == value]
    return compute_summary(filtered, filters, period)
