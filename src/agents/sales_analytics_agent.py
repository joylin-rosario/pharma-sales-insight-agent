"""Sales Analytics Agent (CLAUDE.md section 14).

Invokes deterministic KPI functions/skills and returns structured metrics
only — never generates unsupported business narrative.
"""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from src.analytics.kpi import KPIResult
from src.skills import analyze_business_unit, analyze_territory, calculate_sales_kpis


def run_summary(df: pd.DataFrame, filters: dict[str, Any], period: Optional[str] = None) -> dict[str, KPIResult]:
    return calculate_sales_kpis.run(df, filters, period)


def run_business_unit_analysis(df: pd.DataFrame, business_unit: str | None) -> dict[str, Any]:
    return analyze_business_unit.run(df, business_unit)


def run_territory_analysis(df: pd.DataFrame, territory: str | None = None) -> dict[str, Any]:
    return analyze_territory.run(df, territory)
