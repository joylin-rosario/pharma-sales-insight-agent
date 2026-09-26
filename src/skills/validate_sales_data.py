"""Skill: validate-sales-data. See .claude/skills/validate-sales-data/SKILL.md."""
from __future__ import annotations

import pandas as pd

from src.data.validation import DataQualityReport, validate_dataframe


def run(df: pd.DataFrame) -> DataQualityReport:
    return validate_dataframe(df)
