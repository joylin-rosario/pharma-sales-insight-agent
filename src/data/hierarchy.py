"""Organizational hierarchy integrity checks (CLAUDE.md section 7).

Business Unit > Area > District > Territory > Health Representative.
Each child must map to exactly one parent within the current dataset version.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

import pandas as pd

_CONFIG = json.loads(Path("config/hierarchy.json").read_text())
LEVELS: list[str] = _CONFIG["levels"]
RECONCILIATION_TOLERANCE_PCT: float = _CONFIG["reconciliation_tolerance_pct"]


class HierarchyIssue(NamedTuple):
    level: str
    child: str
    parents: list[str]


def find_ambiguous_mappings(df: pd.DataFrame) -> list[HierarchyIssue]:
    """Return every child value that maps to more than one distinct parent."""
    issues: list[HierarchyIssue] = []
    for i in range(1, len(LEVELS)):
        parent_col, child_col = LEVELS[i - 1], LEVELS[i]
        if parent_col not in df.columns or child_col not in df.columns:
            continue
        mapping = df.groupby(child_col)[parent_col].nunique()
        ambiguous = mapping[mapping > 1]
        for child, _ in ambiguous.items():
            parents = sorted(df.loc[df[child_col] == child, parent_col].unique().tolist())
            issues.append(HierarchyIssue(level=child_col, child=str(child), parents=parents))
    return issues


def reconciliation_ok(df: pd.DataFrame, parent_level: str, child_level: str, value_col: str = "sales_value") -> tuple[bool, float]:
    """Check that summed child totals reconcile to the parent total within tolerance."""
    if parent_level not in df.columns or child_level not in df.columns:
        return True, 0.0
    numeric_values = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    parent_total = numeric_values.sum()
    child_total = numeric_values.groupby(df[child_level]).sum().sum()
    if parent_total == 0:
        return True, 0.0
    diff_pct = abs(parent_total - child_total) / abs(parent_total) * 100
    return bool(diff_pct <= RECONCILIATION_TOLERANCE_PCT), round(float(diff_pct), 4)
