---
name: generate-executive-summary
description: Translate verified KPI results into a structured Facts/Observations/Hypotheses/Recommendations management summary, with limitations and evidence references.
---

# Skill: generate-executive-summary

## Trigger
Invoked by the Insight Agent as the final step before Governance Agent output verification, once Sales Analytics Agent has returned a KPI summary (and optional breakdown).

## Inputs
- `summary`: dict of `KPIResult` from calculate-sales-kpis (and optionally analyze-business-unit / analyze-territory).
- `scope_label`: human-readable description of the current filter scope (e.g. "North Business Unit").
- `period`: label of the period covered, if any.

## Ordered Procedure
1. Build **Facts**: one sentence per KPIResult with a non-null value, each stating the metric, scope, value, and its evidence reference. Facts must come only from deterministic calculations — never invented numbers.
2. Build **Observations**: statements directly supported by two or more Facts (e.g. comparing Achievement % across two Business Units) — never introduce a number not already present in Facts.
3. Build **Hypotheses**: any explanatory statement that goes beyond the data (e.g. "this may be driven by regional demand") must be explicitly prefixed `[HYPOTHESIS - requires human validation]` and never presented as confirmed.
4. Build **Recommendations**: only low-risk, reversible suggestions, each prefixed `[RECOMMENDATION - subject to approval]`; never a hiring/promotion/pay/termination/disciplinary suggestion.
5. Build **Limitations**: list every null-with-reason KPI, every data-quality warning, every reconciliation mismatch, and any incomplete-period comparison used.
6. If no KPIs are available at all (empty summary), stop and state "insufficient evidence" rather than guessing — do not produce Facts/Observations from nothing.
7. Attach the originating `evidence_ids` for every Fact and Observation so the UI/trace can link claims to evidence.

## Output Schema
```
{
  "facts": [str, ...],
  "observations": [str, ...],
  "hypotheses": [str, ...],       // each prefixed [HYPOTHESIS - requires human validation]
  "recommendations": [str, ...],  // each prefixed [RECOMMENDATION - subject to approval]
  "limitations": [str, ...],
  "evidence_ids": [str, ...]
}
```

## Failure Behavior
- If evidence coverage is insufficient (no evidence ids for a claim), the claim is dropped rather than kept unlinked.
- Presenting a Hypothesis as an accepted fact requires a separate human approval (`present_hypothesis_as_fact`) recorded elsewhere in the workflow — this skill never removes the hypothesis label on its own.

## Validation Checklist
- [ ] Every Fact/Observation has a non-null KPIResult and an evidence id
- [ ] Every Hypothesis is explicitly labeled
- [ ] Every Recommendation is explicitly labeled, low-risk, and reversible
- [ ] No prohibited employee-decision or medical content appears
- [ ] No causal language ("caused by", "because of") outside a labeled Hypothesis
- [ ] Limitations list every null/warning/mismatch used
