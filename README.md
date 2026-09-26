# Pharma Sales Insight Agent

A local Agentic AI capstone prototype: an analytics decision-support tool for
pharmaceutical sales business users. Upload sales data, get evidence-based,
governed KPI insights across the Business Unit → Area → District → Territory
→ Health Representative hierarchy. **This is a decision-support prototype,
not a chatbot or autonomous decision-maker** — see `CLAUDE.md` for the full
governing specification.

## Architecture

- **Supervisor** (`src/orchestrator.py`, `SalesInsightSupervisor`): understands
  a question, builds a plan, delegates to sub-agents, verifies output, persists
  state, and logs a trace — all deterministically, no LLM API call at runtime.
- **Sub-agents** (`src/agents/`): Data Quality, Sales Analytics, Insight, Governance.
- **Skills** (`.claude/skills/`): validate-sales-data, calculate-sales-kpis,
  analyze-business-unit, analyze-territory, generate-executive-summary.
- **Deterministic KPI math** (`src/analytics/kpi.py`): every number is computed
  in Python, never generated as free-form text.
- **Guardrails & approval** (`src/governance/`): blocks prohibited employee
  decisions, medical advice, PII/PHI, prompt injection, and out-of-scope access;
  gates exports, HR-level detail, hierarchy corrections, hypothesis-as-fact
  presentation, and connector/write actions behind recorded human approval.
- **State & trace** (`src/state/`, `src/observability/`): a Pydantic
  `WorkflowState` per request, persisted to SQLite, with a JSON Lines
  observability log rendered as an execution timeline in the UI.

Why no LLM API call at runtime? CLAUDE.md requires "Calculate all authoritative
metrics in Python, never in free-form LLM text" and "Generate insights only
from verified calculations." Intent parsing and narrative generation are
implemented as deterministic, testable, rule-based Python instead — this keeps
the prototype reproducible, free of fabrication risk, and deployable without
any API key.

## Setup

Requires Python 3.11+.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open the printed local URL (typically http://localhost:8501). In the **Upload**
tab, click "Load synthetic demo dataset" or upload your own CSV/XLSX matching
the data contract in `CLAUDE.md` section 8.

## Test

```bash
pytest -q
```

42 tests covering KPI formulas (incl. zero-denominator cases), hierarchy
reconciliation and ambiguity detection, data-quality pass/warning/block paths,
every guardrail check, full orchestrator integration, and a golden set of
Business Unit / Territory / management-summary questions.

## Demo script

1. **Upload** — load the synthetic dataset (120 rows across 2 Business Units).
2. **Data Quality** — confirm status is PASS with no issues.
3. **Dashboard** — filter by Business Unit/Area/Territory/Product/Period,
   view KPI cards and charts.
4. **Ask** — ask "What is our achievement percent versus target this period?"
   or "Which territories are top and bottom performers?" — watch the plan,
   delegation, and Facts/Observations/Hypotheses/Recommendations/Limitations
   render with evidence references.
5. Try a prohibited question (e.g. "should we fire the underperforming rep?")
   — confirm it is blocked with a responsible explanation.
6. **Approval** — approve the pending action, then return to **Ask** and export
   the management report (export is disabled until approval is recorded).
7. **Trace** — view the full execution timeline for the request.

## Repository structure

See `CLAUDE.md` section 12 for the authoritative structure. Config lives in
`config/`, synthetic demo data in `data/synthetic/`, Claude Code dev-time
sub-agent/skill/hook definitions in `.claude/`.

## Known simplifications (documented, not hidden)

- The supervisor's "retry once on recoverable failure" is implemented as a
  single try/except with an early, limitations-only return on failure, rather
  than a full replanning loop.
- MCP server wiring (section 17) is not implemented in this vertical slice;
  SQLite/filesystem access is direct but scoped to read-only workflow state
  and project data/output folders, consistent with the least-privilege intent.
- Intent parsing and narrative generation are rule-based, not LLM-driven — see
  Architecture above for why.

## Deployment

This app has no secrets and only ships with synthetic demo data, so it can be
deployed to Streamlit Community Cloud directly from this repository — see the
deployment instructions provided alongside this repo, or deploy manually at
https://share.streamlit.io by pointing at this repo's `app.py` on `main`.
