# PROGRESS

## Status: Full vertical slice complete (Definition of Done, CLAUDE.md section 27)

Build scope was confirmed with the user as: create a GitHub repo and push
(user performs the final Streamlit Community Cloud "Deploy" click), and
implement the full vertical slice per the Definition of Done rather than
every optional item in the 28-section spec.

## Completed

- **Phase 1 — scaffold**: repo structure, `requirements.txt` (pinned),
  `config/{hierarchy,kpi_config,guardrails,roles}.json`, synthetic dataset
  generator (`data/synthetic/generate_data.py`, 120 rows, 2 Business Units),
  deterministic KPI functions (`src/analytics/kpi.py`).
- **Phase 2 — Streamlit UI**: `app.py` with Upload, Data Quality, Dashboard,
  Ask, Approval, Trace tabs; cascading hierarchy filters; role/scope sidebar;
  KPI cards; Plotly charts styled via a validated categorical/status palette
  (`src/ui/palette.py`); HR-name masking in row-level views.
- **Phase 3 — agentic core**: `SalesInsightSupervisor` (`src/orchestrator.py`)
  implementing understand → plan → delegate → verify; 4 sub-agents
  (`src/agents/`); 5 skills (`src/skills/` + `.claude/skills/*/SKILL.md`);
  Pydantic `WorkflowState` (`src/state/models.py`) persisted to SQLite.
- **Phase 4 — governance**: guardrails (`src/governance/guardrails.py`) for
  prohibited employee decisions/inference, medical/clinical, PII/PHI,
  prompt injection, causation language, and scope; approval gate
  (`src/governance/approval.py`) for the 5 required actions; JSONL
  observability log + Trace tab; `.claude/hooks/` (SessionStart,
  UserPromptSubmit, PreToolUse, PostToolUse, SubagentStart/Stop, Stop) wired
  via `.claude/settings.json`, all fail-safe by design.
- **Phase 5 — verification**: 42 pytest tests, all passing (KPI formulas incl.
  zero-denominator edge cases, hierarchy reconciliation/ambiguity, data
  validation pass/warning/block, all guardrails, orchestrator integration,
  golden set). End-to-end smoke test via headless Chrome + Playwright:
  Upload → Data Quality (PASS, 120 rows) → Dashboard (correct KPI values and
  chart styling) → Ask (plan + delegation + evidence-linked Facts/Observations
  rendered correctly) → Trace (full execution timeline rendered) — zero
  browser console errors throughout.

## Test results (latest run)

```
42 passed in 0.81s
```

## Key decisions and assumptions

- No LLM API call at runtime: intent parsing and narrative generation are
  deterministic/rule-based Python, not an LLM call, to satisfy "calculate all
  authoritative metrics in Python, never in free-form LLM text" and to avoid
  any API-key dependency for local + cloud deployment. Documented in README.
- Supervisor's "retry once" requirement is currently a single try/except with
  an early limitations-only return, not a full replan loop — documented as a
  known simplification in README rather than silently omitted.
- MCP server wiring (section 17) was not built; the app's own read-only
  SQLite/filesystem access already satisfies the least-privilege intent for
  this local prototype. Flagged as a possible next-phase item, not hidden.
- GitHub repo visibility defaulted to public, since the repository contains
  only synthetic data and no secrets; confirm with the user before ongoing use
  if this should instead be private.

## Known minor gaps (not yet fixed)

- The "Load synthetic demo dataset" button path does not show the same
  "Loaded N rows" success message as the file-uploader path (cosmetic only;
  discovered during Playwright smoke testing).

## Next steps (if continuing beyond this capstone submission)

1. Implement a true retry/replan loop in the supervisor for recoverable
   step failures.
2. Add the read-only SQLite / filesystem MCP server wiring described in
   section 17, with an explicit allowlist.
3. Fix the demo-load button success-message asymmetry.
4. Expand the golden set and add latency/cost tracking to the observability
   log once real usage patterns are known.
