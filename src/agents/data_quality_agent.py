"""Data Quality Agent (CLAUDE.md section 14)."""
from __future__ import annotations

import pandas as pd

from src.skills import validate_sales_data
from src.state.models import DataQualityStatus


def run(df: pd.DataFrame):
    report = validate_sales_data.run(df)
    return report, DataQualityStatus(report.status)
