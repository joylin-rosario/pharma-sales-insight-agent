"""Deterministic KPI calculations (CLAUDE.md section 9). Pure Python/Pandas —
never computed by free-form LLM text.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel

_CONFIG = json.loads(Path("config/kpi_config.json").read_text())
CURRENCY_DECIMALS = _CONFIG["currency_decimals"]
PERCENT_DECIMALS = _CONFIG["percent_decimals"]


class KPIResult(BaseModel):
    metric: str
    filters: dict[str, Any]
    period: Optional[str] = None
    value: Optional[float] = None
    reason: Optional[str] = None
    display: Optional[str] = None


def actual_sales(df: pd.DataFrame) -> float:
    return float(pd.to_numeric(df["sales_value"], errors="coerce").fillna(0).sum())


def target_sales(df: pd.DataFrame) -> float:
    return float(pd.to_numeric(df["target_value"], errors="coerce").fillna(0).sum())


def achievement_pct(actual: float, target: float) -> tuple[Optional[float], Optional[str]]:
    if target == 0:
        return None, "Target Sales is zero or unavailable; Achievement % is undefined."
    return actual / target * 100, None


def variance_to_target(actual: float, target: float) -> float:
    return actual - target


def growth_pct(current: float, prior: Optional[float]) -> tuple[Optional[float], Optional[str]]:
    if prior is None or prior == 0:
        return None, "Prior period sales is zero or unavailable; Growth % is undefined."
    return (current - prior) / prior * 100, None


def contribution_pct(entity_sales: float, parent_sales: float) -> tuple[Optional[float], Optional[str]]:
    if parent_sales == 0:
        return None, "Parent Sales is zero or unavailable; Contribution % is undefined."
    return entity_sales / parent_sales * 100, None


def round_currency(value: float) -> float:
    return round(value, CURRENCY_DECIMALS)


def round_percent(value: float) -> float:
    return round(value, PERCENT_DECIMALS)


def compute_summary(df: pd.DataFrame, filters: dict[str, Any], period: Optional[str] = None) -> dict[str, KPIResult]:
    """Full precision retained internally; display strings rounded per section 9."""
    actual = actual_sales(df)
    target = target_sales(df)
    ach, ach_reason = achievement_pct(actual, target)
    variance = variance_to_target(actual, target)

    prior_total: Optional[float] = None
    if "prior_period_sales" in df.columns:
        prior_series = pd.to_numeric(df["prior_period_sales"], errors="coerce")
        if prior_series.notna().any():
            prior_total = float(prior_series.fillna(0).sum())
    growth, growth_reason = growth_pct(actual, prior_total)

    results = {
        "actual_sales": KPIResult(
            metric="actual_sales", filters=filters, period=period, value=actual,
            display=f"${round_currency(actual):,.2f}",
        ),
        "target_sales": KPIResult(
            metric="target_sales", filters=filters, period=period, value=target,
            display=f"${round_currency(target):,.2f}",
        ),
        "achievement_pct": KPIResult(
            metric="achievement_pct", filters=filters, period=period, value=ach, reason=ach_reason,
            display=f"{round_percent(ach)}%" if ach is not None else "N/A",
        ),
        "variance_to_target": KPIResult(
            metric="variance_to_target", filters=filters, period=period, value=variance,
            display=f"${round_currency(variance):,.2f}",
        ),
        "growth_pct": KPIResult(
            metric="growth_pct", filters=filters, period=period, value=growth, reason=growth_reason,
            display=f"{round_percent(growth)}%" if growth is not None else "N/A",
        ),
    }
    return results


def compute_contribution_breakdown(df: pd.DataFrame, group_col: str, filters: dict[str, Any]) -> list[KPIResult]:
    parent_total = actual_sales(df)
    out: list[KPIResult] = []
    for key, group in df.groupby(group_col):
        entity_sales = actual_sales(group)
        pct, reason = contribution_pct(entity_sales, parent_total)
        out.append(
            KPIResult(
                metric="contribution_pct",
                filters={**filters, group_col: key},
                value=pct,
                reason=reason,
                display=f"{round_percent(pct)}%" if pct is not None else "N/A",
            )
        )
    return sorted(out, key=lambda r: (r.value is None, -(r.value or 0)))
