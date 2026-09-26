---
name: validate-sales-data
description: Validate an uploaded pharmaceutical sales file for schema, types, completeness, duplicates, and hierarchy integrity before any analysis runs.
---

# Skill: validate-sales-data

## Trigger
Invoked by the Data Quality Agent immediately after a file is loaded via `src/data/ingestion.py`, before any KPI calculation or question answering is permitted.

## Inputs
- `df`: pandas DataFrame with normalized (snake_case) headers.
- `dataset_version`: hash identifying the uploaded file version.

## Ordered Procedure
1. Normalize headers to snake_case (already done at ingestion) — never alter source values.
2. Check that all required columns from the data contract are present (`date, business_unit, area, district, territory, hr_id, hr_name, product, sales_value, target_value`). Missing required column → **block**.
3. Check the DataFrame is non-empty. Empty → **block**.
4. Check numeric columns (`sales_value, target_value, prior_period_sales, units_sold`) contain only numeric values. Non-numeric value found → **block**. Negative value found → **warning**.
5. Check completeness: required columns must have no nulls. Null found in a required column → **block**.
6. Check duplicates on the natural key `[date, territory, hr_id, product]`. Duplicate found → **warning**.
7. Check hierarchy integrity: every child level must map to exactly one parent (Business Unit > Area > District > Territory > HR). Ambiguous mapping found → **block**.
8. Check parent/child reconciliation (Business Unit vs Area totals) within the configured tolerance. Out of tolerance → **warning**.
9. Compute overall status = the most severe of all findings (`block` > `warning` > `pass`).

## Output Schema
`DataQualityReport` (see `src/data/validation.py`):
```
{
  "status": "pass" | "warning" | "block",
  "row_count": int,
  "findings": [{"severity": "block"|"warning", "check": str, "message": str, "details": dict|null}]
}
```

## Failure Behavior
- Any `block` finding stops the workflow: dashboards, filters, and the Ask tab must not run against this dataset. The UI surfaces the findings and does not silently proceed.
- `warning` findings are shown but do not block; they must appear in Limitations if referenced later.
- Never fabricate a pass result — if validation cannot run (e.g. unreadable file), return `block` with the underlying error message.

## Validation Checklist
- [ ] All required columns present
- [ ] No empty dataset
- [ ] Numeric columns are numeric; negatives flagged
- [ ] No nulls in required columns
- [ ] Duplicates on natural key flagged
- [ ] No ambiguous child→parent hierarchy mappings
- [ ] Parent/child totals reconcile within tolerance
- [ ] Overall status correctly reflects the most severe finding
