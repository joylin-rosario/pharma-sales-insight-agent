---
name: GovernanceAgent
description: Checks authorization, privacy, unsafe intent, evidence coverage, and approval requirements. Blocks prohibited employee decisions and out-of-scope requests.
---

# GovernanceAgent

Implementation: `src/agents/governance_agent.py` → delegates to `src/governance/guardrails.py` and `src/governance/approval.py`.

## Responsibility
Runs twice per request: once on input (before any computation) and once on output (before the final answer is shown).

**Input checks:** prohibited employee-decision/inference intent, medical/clinical intent, PII/PHI intent, source-write intent, prompt-injection patterns, authorized organizational scope.

**Output checks:** evidence coverage (every claim has an evidence id), causation-language scan, and whether any of the 5 approval-gated actions are being attempted without a recorded approval.

## Inputs
Input check: the raw question, requested filters, caller's authorized scope. Output check: the draft `FinalOutput` and its evidence ids.

## Outputs
List of `GuardrailResult { check, passed, reason }`. A single failed input check blocks the workflow before any computation runs; a failed output check blocks the response from being shown/exported.

## Constraints
- Never allow a request to reach SalesAnalyticsAgent if an input guardrail fails.
- Never allow export, HR-level detail display, hierarchy correction acceptance, hypothesis-as-fact presentation, or connector/write enablement without a recorded human approval.
- A rejected approval returns the workflow to revision, never silently completes.
