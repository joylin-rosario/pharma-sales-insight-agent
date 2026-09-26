"""Data quality validation (CLAUDE.md section 4 step 2 and section 14).

Checks schema, types, completeness, duplicates, numeric ranges, and hierarchy
integrity. Returns pass / warning / block with evidence, per the Data
Quality Agent's contract.
"""
from __future__ import annotations

import pandas as pd
from pydantic import BaseModel

from src.data.hierarchy import find_ambiguous_mappings, reconciliation_ok
from src.data.schema import NUMERIC_COLUMNS, REQUIRED_COLUMNS


class ValidationFinding(BaseModel):
    severity: str  # info | warning | block
    check: str
    message: str


class DataQualityReport(BaseModel):
    status: str  # pass | warning | block
    findings: list[ValidationFinding]
    row_count: int
    checked_columns: list[str]


def validate_dataframe(df: pd.DataFrame) -> DataQualityReport:
    findings: list[ValidationFinding] = []

    missing_required = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_required:
        findings.append(
            ValidationFinding(
                severity="block",
                check="required_columns",
                message=f"Missing required columns: {', '.join(missing_required)}",
            )
        )
        return DataQualityReport(
            status="block", findings=findings, row_count=len(df), checked_columns=list(df.columns)
        )

    if df.empty:
        findings.append(ValidationFinding(severity="block", check="row_count", message="File contains no rows."))
        return DataQualityReport(status="block", findings=findings, row_count=0, checked_columns=list(df.columns))

    # Types / numeric ranges
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        bad = coerced.isna() & df[col].notna() & (df[col] != "")
        if bad.any():
            findings.append(
                ValidationFinding(
                    severity="block",
                    check="numeric_type",
                    message=f"Column '{col}' has {int(bad.sum())} non-numeric value(s).",
                )
            )
        elif col in ("sales_value", "target_value"):
            negative = coerced.dropna() < 0
            if negative.any():
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        check="numeric_range",
                        message=f"Column '{col}' has {int(negative.sum())} negative value(s).",
                    )
                )

    # Completeness on required columns (excluding numeric optional-by-nature prior_period_sales)
    for col in REQUIRED_COLUMNS:
        nulls = df[col].isna().sum() + (df[col] == "").sum()
        if nulls > 0:
            findings.append(
                ValidationFinding(
                    severity="block",
                    check="completeness",
                    message=f"Column '{col}' has {int(nulls)} missing value(s).",
                )
            )

    # Duplicates on natural key
    natural_key = [c for c in ["date", "territory", "hr_id", "product"] if c in df.columns]
    if natural_key:
        dup_count = int(df.duplicated(subset=natural_key).sum())
        if dup_count > 0:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    check="duplicates",
                    message=f"Found {dup_count} duplicate row(s) on key {natural_key}.",
                )
            )

    # Hierarchy integrity
    ambiguous = find_ambiguous_mappings(df)
    for issue in ambiguous:
        findings.append(
            ValidationFinding(
                severity="block",
                check="hierarchy_mapping",
                message=f"'{issue.child}' ({issue.level}) maps to multiple parents: {issue.parents}.",
            )
        )

    ok, diff_pct = reconciliation_ok(df, "business_unit", "area")
    if not ok:
        findings.append(
            ValidationFinding(
                severity="warning",
                check="reconciliation",
                message=f"Business Unit vs Area sales totals differ by {diff_pct}% (tolerance exceeded).",
            )
        )

    if any(f.severity == "block" for f in findings):
        status = "block"
    elif any(f.severity == "warning" for f in findings):
        status = "warning"
    else:
        status = "pass"

    return DataQualityReport(
        status=status, findings=findings, row_count=len(df), checked_columns=list(df.columns)
    )
