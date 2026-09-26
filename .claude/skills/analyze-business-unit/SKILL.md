---
name: analyze-business-unit
description: Produce a Business Unit-level performance breakdown (achievement, variance, area contribution) for Sales Head and Area Manager questions.
---

# Skill: analyze-business-unit

## Trigger
Invoked by the Sales Analytics Agent when the parsed intent's `level` is `business_unit` (e.g. "How is the North Business Unit performing against target?").

## Inputs
- `df`: validated DataFrame scoped to the caller's authorized Business Unit(s).
- `filters`: dict, must include `business_unit` when the caller is not a Sales Head with enterprise scope.
- `period` (optional).

## Ordered Procedure
1. Confirm the requested Business Unit is within the caller's `authorized_scope` (Governance Agent responsibility upstream; this skill assumes it has already passed).
2. Call `calculate-sales-kpis` for Actual, Target, Achievement %, Variance, and Growth % at the Business Unit level.
3. Call `compute_contribution_breakdown(df, group_col="area", filters)` to rank Areas by contribution % within the Business Unit.
4. Verify Area totals reconcile to the Business Unit total within tolerance (`src/data/hierarchy.reconciliation_ok`); if not, add a limitation rather than presenting the breakdown as exact.
5. Return the KPI set plus the ranked Area breakdown, each wrapped as evidence-linked `KPIResult`s.

## Output Schema
```
{
  "summary": {"actual_sales": KPIResult, "target_sales": KPIResult, "achievement_pct": KPIResult, "variance_to_target": KPIResult, "growth_pct": KPIResult},
  "area_breakdown": [KPIResult, ...]  // sorted by contribution % descending
}
```

## Failure Behavior
- Out-of-scope Business Unit requests are never reached by this skill (blocked earlier by the Governance Agent); if somehow invoked out of scope, return no results and raise a governance error rather than compute.
- Reconciliation mismatches beyond tolerance are reported as a limitation, not hidden.

## Validation Checklist
- [ ] Scope checked before computation (defense in depth even though Governance Agent gates first)
- [ ] KPIs computed via calculate-sales-kpis, not inline
- [ ] Area breakdown sorted and evidence-linked
- [ ] Reconciliation checked; mismatches surfaced as limitations
