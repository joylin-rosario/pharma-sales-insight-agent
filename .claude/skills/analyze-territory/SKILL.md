---
name: analyze-territory
description: Identify top or bottom performing territories using objective sales metrics, and support Territory Manager drill-down questions.
---

# Skill: analyze-territory

## Trigger
Invoked by the Sales Analytics Agent when the parsed intent's `level` is `territory`, or the question asks to "identify top/bottom territories."

## Inputs
- `df`: validated DataFrame scoped to the caller's authorized Territory/Territories.
- `filters`: dict, must include `territory` when the caller is a Territory Manager (single-territory scope).
- `top_n` (optional, default 3): number of top/bottom entries to return.

## Ordered Procedure
1. Confirm requested Territory/Territories are within the caller's authorized scope.
2. Call `calculate-sales-kpis` for Actual, Target, Achievement %, and Variance at the Territory level.
3. Group by `territory` (`df.groupby("territory")`) and rank by Actual Sales to produce top-N and bottom-N lists.
4. Never rank using employee-attributed metrics as a proxy for HR performance — territory ranking only, no inference about the Health Representative's competence or effort.
5. If the caller is authorized to view HR-level detail AND the `view_hr_level_detail` approval has been granted, optionally include HR-level rows within the territory; otherwise mask HR identifiers.
6. Return ranked results wrapped as evidence-linked `KPIResult`s.

## Output Schema
```
{
  "summary": {"actual_sales": KPIResult, "target_sales": KPIResult, "achievement_pct": KPIResult, "variance_to_target": KPIResult},
  "top_territories": [KPIResult, ...],
  "bottom_territories": [KPIResult, ...]
}
```

## Failure Behavior
- Must never produce a ranking that implies causation ("Territory X underperforms because Rep Y is weak") — rankings are descriptive sales facts only.
- HR-level names are masked unless both role permission and explicit approval are present; failing that check returns masked identifiers, not an error.

## Validation Checklist
- [ ] Scope checked before computation
- [ ] Ranking based only on objective sales metrics (Actual Sales / Achievement %), never inferred attributes
- [ ] HR identifiers masked unless approved and authorized
- [ ] No causal language in output labels
