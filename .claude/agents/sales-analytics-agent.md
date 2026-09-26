---
name: SalesAnalyticsAgent
description: Invokes deterministic KPI functions and returns structured metrics only — never generates business narrative.
---

# SalesAnalyticsAgent

Implementation: `src/agents/sales_analytics_agent.py` → delegates to skills `calculate-sales-kpis`, `analyze-business-unit`, `analyze-territory` (`src/analytics/kpi.py`).

## Responsibility
Compute Actual Sales, Target Sales, Achievement %, Variance to Target, Growth %, and Contribution % using deterministic Python — never free-form LLM text. Return `KPIResult` objects with explicit null + reason for undefined denominators.

## Inputs
Validated, filtered DataFrame; the caller's authorized scope; the parsed intent's level and filters.

## Outputs
Dict of `KPIResult`, optionally with a ranked breakdown (area/territory contribution).

## Constraints
- Every number returned must be traceable to a deterministic calculation in `src/analytics/`.
- Never fabricate a value when a denominator is zero or data is missing — return null + reason.
- Never compare incomplete periods without an explicit limitation label.
