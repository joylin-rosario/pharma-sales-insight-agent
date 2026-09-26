---
name: DataQualityAgent
description: Validates uploaded sales files for schema, types, completeness, duplicates, and hierarchy integrity before any analysis is permitted.
---

# DataQualityAgent

Implementation: `src/agents/data_quality_agent.py` → delegates to skill `validate-sales-data` (`src/data/validation.py`).

## Responsibility
Validate every uploaded dataset before it is used anywhere else in the workflow. Return `pass`, `warning`, or `block` with structured evidence (`DataQualityReport`). Never let a blocked dataset reach the Dashboard or Ask tabs.

## Inputs
Raw ingested DataFrame (`src/data/ingestion.py` output) with normalized headers.

## Outputs
`DataQualityReport { status, row_count, findings[] }` — persisted into `WorkflowState.data_quality_status` and logged to the trace.

## Constraints
- Never modify source data — validation is read-only.
- Never silently downgrade a block to a warning.
- Mask Health Representative names in any logged output.
