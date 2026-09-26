"""Skill: analyze-territory. See .claude/skills/analyze-territory/SKILL.md."""
from __future__ import annotations

from typing import Any

import pandas as pd

from src.analytics.kpi import KPIResult, actual_sales, compute_summary


def run(df: pd.DataFrame, territory: str | None = None, top_n: int = 5, bottom_n: int = 5) -> dict[str, Any]:
    if territory:
        scoped = df[df["territory"] == territory]
        summary = compute_summary(scoped, {"territory": territory})
        return {"summary": summary}

    ranked = (
        df.groupby("territory")
        .apply(lambda g: actual_sales(g), include_groups=False)
        .sort_values(ascending=False)
    )
    return {
        "top": ranked.head(top_n).to_dict(),
        "bottom": ranked.tail(bottom_n).to_dict(),
    }
