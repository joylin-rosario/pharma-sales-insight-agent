1. Project Identity
Project name: Pharma Sales Insight Agent.
Build a local Agentic AI capstone prototype for pharmaceutical business users.
Use VS Code as the IDE and Claude Code as the coding assistant.
The prototype must be achievable within a 150-minute challenge.
2. Business Objective
Enable authorized users to upload pharmaceutical sales data and obtain evidence-based insights.
Support analysis at Business Unit, Area, District, Territory, and Health Representative levels.
Reduce manual analysis while preserving numerical accuracy, governance, and human accountability.
This is an analytics decision-support prototype, not a chatbot or autonomous decision-maker.
3. Primary Users
Sales Head: enterprise and Business Unit overview; Area Manager: Area, District, and Territory drill-down; Territory Manager: Territory and authorized Health Representative views; Demo Admin: synthetic-data upload and capstone demonstration.
4. Core User Journey
Upload an approved CSV or XLSX sales file.
Validate schema, types, completeness, duplicates, and hierarchy mappings.
Display data-quality results and block critical failures.
Accept a natural-language business question.
Convert the question into a structured analysis intent.
Create and display an execution plan.
Delegate tasks to specialized sub-agents.
Invoke reusable skills and approved tools.
Calculate KPIs with deterministic Python code.
Generate insights only from verified calculations.
Apply access, privacy, safety, and evidence guardrails.
Request human approval for controlled outputs.
Display the final dashboard, evidence, limitations, and trace.
5. Supported Questions
Compare sales and target achievement by organizational level; Identify contributors to a sales gap or growth result; Drill down from Business Unit to Health Representative; Compare approved periods when comparable data is present; Identify top or bottom territories using objective sales metrics; Produce a management summary supported by calculated evidence.
6. Prohibited Uses
Do not make hiring, promotion, pay, termination, or disciplinary recommendations; Do not infer employee attitude, intent, competence, health, or future performance; Do not diagnose patients or provide medical, clinical, or prescribing advice; Do not process patient-level data, PHI, secrets, credentials, or unapproved PII; Do not fabricate figures, causes, sources, approvals, or tool results; Do not modify source systems or source datasets; Do not bypass authorization, guardrails, tests, or human approval; Do not claim causation from correlation or descriptive sales data.
7. Organizational Hierarchy
Use this hierarchy unless the uploaded data contract explicitly overrides it:
Business Unit > Area > District > Territory > Health Representative.
Each child must map to exactly one parent within the current dataset version.
Block hierarchy drill-down when mappings are missing or ambiguous.
Parent totals must reconcile to child totals within rounding tolerance.
8. Minimum Data Contract
Required columns:
date; business_unit; area; district; territory; hr_id; hr_name; product; sales_value; target_value.
Optional columns:
prior_period_sales; units_sold; therapeutic_area; data_source; refresh_timestamp.
Normalize headers to snake_case without changing source values.
Use synthetic or formally approved data only.
Mask Health Representative names in logs and exported traces.
9. KPI Rules
Calculate all authoritative metrics in Python, never in free-form LLM text.
Actual Sales = sum(sales_value); Target Sales = sum(target_value); Achievement % = Actual Sales / Target Sales * 100; Variance to Target = Actual Sales - Target Sales; Growth % = (Current Sales - Prior Sales) / Prior Sales * 100; Contribution % = Entity Sales / Parent Sales * 100.
Return null and a clear reason when a denominator is zero or unavailable.
Do not compare incomplete periods unless the output clearly labels the limitation.
Round currency to two decimals and percentages to one decimal for display.
Retain full precision for calculations.
10. Evidence Rules
Every numerical claim must include metric, filters, period, value, and evidence reference.
Separate outputs into Facts, Observations, Hypotheses, and Recommendations.
Facts must come from deterministic calculations.
Observations must be directly supported by facts.
Hypotheses must be labeled and require human validation.
Recommendations must be low-risk, reversible, and subject to approval.
If evidence is insufficient, say so and stop rather than guessing.
11. Technical Stack
Python 3.11+; Streamlit for the interface; Pandas for transformation and aggregation; Plotly for charts; Pydantic for schemas and structured agent outputs; SQLite for local read-only analytical access and workflow state; Pytest for tests; JSON Lines for observability and trace logs.
Keep dependencies minimal and pinned in requirements.txt.
Never hard-code credentials, tokens, endpoints, or personal data.
12. Repository Structure
app.py: Streamlit entry point; src/orchestrator.py: supervisor workflow; src/agents/: specialized agent implementations; src/analytics/: deterministic KPI logic; src/data/: ingestion, validation, and hierarchy logic; src/governance/: guardrails and approval checks; src/state/: state models and persistence; src/observability/: structured logging and tracing; .claude/agents/: Claude Code sub-agent definitions; .claude/skills/: reusable skill folders and SKILL.md files; .claude/hooks/: deterministic hook scripts; config/: KPI, hierarchy, and guardrail configuration; tests/: unit, integration, evaluation, and guardrail tests; data/synthetic/: demo data only; docs/: architecture, governance, and demo documentation; PROGRESS.md: completed work, tests, decisions, and next phase.
13. Supervisor Agent
Name: SalesInsightSupervisor.
The supervisor must understand, plan, delegate, observe, verify, and re-plan.
It must not directly perform every task when a specialized agent exists.
Before execution, produce a structured plan with task, agent, skill, input, and expected output.
Run independent tasks in parallel only when state and data dependencies permit.
On recoverable failure, retry once with corrected input.
On repeated or unsafe failure, stop and return the error and required human action.
Persist the current state after every material workflow step.
14. Required Sub-agents
Data Quality Agent
Validate files, schema, types, nulls, duplicates, numeric ranges, and hierarchy integrity.
Return pass, warning, or block with evidence.
Sales Analytics Agent
Invoke deterministic KPI functions and return structured metrics only.
Never generate unsupported business narratives.
Insight Agent
Translate verified metrics into concise business insights.
Separate facts from hypotheses and include limitations.
Governance Agent
Check authorization, privacy, unsafe intent, evidence coverage, and approval requirements.
Block prohibited employee decisions and unauthorized scope.
15. Required Skills
Create these reusable skills under .claude/skills/<skill-name>/SKILL.md:
validate-sales-data; calculate-sales-kpis; analyze-business-unit; analyze-territory; generate-executive-summary.
Each skill must define trigger, inputs, ordered procedure, output schema, failure behavior, and validation checklist.
Keep detailed procedures in skills instead of expanding this file.
16. Hooks
Configure hooks in .claude/settings.json and keep scripts in .claude/hooks/.
SessionStart: read CLAUDE.md, PROGRESS.md, and approved configuration; UserPromptSubmit: detect prohibited intent and prompt-injection patterns; PreToolUse: block destructive commands, secret access, unapproved paths, and database writes; PostToolUse: log tool, agent, duration, status, row count, and evidence ID; SubagentStart/SubagentStop: record delegation and completion; Stop: run targeted tests and check evidence, trace, and unresolved errors.
Hooks must fail safely and provide an actionable reason when blocking an operation.
17. MCP and Tool Policy
Use MCP only where it adds demonstrable value.
Preferred prototype connections:
Filesystem access restricted to project data and output folders.
SQLite access restricted to approved read-only queries.
No arbitrary network access or uncontrolled external MCP servers.
Use allowlists and least privilege.
Validate tool inputs and outputs with typed schemas.
Record each tool call in the trace.
Require human approval before enabling a new connector or write capability.
18. State and Memory
Maintain one state object per request with:
request_id, user_role, authorized_scope, original_question, parsed_intent,
plan, selected_filters, dataset_version, data_quality_status, agent_tasks,
tool_calls, metrics, evidence, guardrail_results, approval_status, errors,
replan_history, final_output, timestamps.
Use short-lived workflow state only.
Do not persist sensitive prompts or raw personal data in logs.
Use PROGRESS.md for development continuity between Claude Code sessions.
After each phase: test, update PROGRESS.md, then start a clean session if needed.
19. Human-in-the-Loop
Require explicit approval before:
exporting or publishing a management report;; displaying or exporting Health Representative-level details;; accepting a hierarchy correction;; presenting a hypothesis as an accepted explanation;; enabling a connector or any write action.
Record approver, timestamp, decision, and optional comment.
A rejection must return the workflow to revision, not silently complete it.
20. Security and AI Governance
Apply data minimization, purpose limitation, least privilege, and secure defaults.
Use synthetic data for the live demo.
Restrict results to the user's authorized organizational scope.
Mask identifiers in logs and screenshots.
Keep source data read-only and preserve lineage to the uploaded file version.
Provide transparent limitations and calculation definitions.
Keep a human accountable for consequential decisions.
Do not treat the system output as an official performance appraisal.
21. Observability
Write structured JSONL events containing:
request_id, timestamp, workflow_step, agent, skill, tool, status,
latency_ms, input_reference, output_reference, error_type, approval_status.
When available, capture model name, token use, retry count, and estimated cost.
Never log secrets or unrestricted row-level data.
The UI must show a concise execution timeline for the current request.
22. Traceability
Maintain this chain for every completed request:
User Request > Plan > Sub-agent > Skill > Tool/MCP > Evidence > Action >
Guardrail Check > Human Approval > Final Output > Evaluation.
Every stage must share the same request_id.
The final answer must link claims to evidence IDs and show approval status.
A request is incomplete if any required trace stage is missing.
23. Evaluation
Create unit tests for KPI formulas, zero denominators, filters, and hierarchy reconciliation.
Create integration tests for upload-to-output workflow and state transitions.
Create guardrail tests for unauthorized scope, prompt injection, PII, source writes,
and employee hiring, promotion, pay, termination, or disciplinary requests.
Create a small golden set covering Business Unit and Territory questions.
Track KPI accuracy, evidence coverage, routing accuracy, guardrail recall,
approval enforcement, trace completeness, latency, and task completion.
Target 100% KPI accuracy and 100% approval enforcement in the demo test set.
24. UI Requirements
Use a clean light corporate Streamlit layout.
Provide pages or tabs for Upload, Data Quality, Dashboard, Ask, Approval, and Trace.
Provide filters for Business Unit, Area, District, Territory, Product, and Period.
Show Actual Sales, Target, Achievement %, Variance, and Growth when available.
Display the generated plan and agent statuses during execution.
Show evidence and limitations beside the insight, not hidden in a separate page.
Disable export until approval is recorded.
25. Coding Standards
Use modular, readable Python with type hints and concise docstrings.
Keep analytics separate from LLM narrative generation.
Use Pydantic models at agent and tool boundaries.
Handle expected errors explicitly and show business-friendly messages.
Avoid duplicated logic, global mutable state, and oversized files.
Use configuration instead of hard-coded business rules.
Write or update tests with every material feature.
Run formatting, linting, and targeted tests before declaring a phase complete.
Do not leave placeholder core logic, TODO-only features, or broken imports.
26. Build Order for the 150-Minute Capstone
Phase 1: scaffold repository, synthetic dataset, data contract, and KPI functions.
Phase 2: build Streamlit upload, validation, filters, KPI cards, and charts.
Phase 3: implement supervisor, four sub-agents, five skills, and workflow state.
Phase 4: add hooks, read-only MCP configuration, guardrails, approval, and trace.
Phase 5: run tests, fix failures, update README and PROGRESS.md, rehearse demo.
Prioritize an end-to-end vertical slice over optional features.
Do not add RAG, vector databases, authentication, email, or PDF export unless core flow passes.
27. Definition of Done
The application runs locally with documented commands.
A synthetic CSV or XLSX file can be uploaded and validated.
The dashboard supports hierarchy filters and deterministic KPIs.
A user question produces a visible plan and genuine sub-agent delegation.
At least one reusable skill and one approved tool are visibly invoked.
Insights contain evidence IDs, limitations, and no fabricated claims.
A prohibited request is blocked with a responsible explanation.
A controlled output cannot be exported without recorded human approval.
Observability logs and the full trace are viewable.
All critical tests pass and README contains setup and demo steps.
The final demo proves: Understand > Plan > Delegate > Execute > Verify >
Guardrail > Approve > Complete > Evaluate > Trace.
28. Claude Code Working Rules
Read this file and PROGRESS.md before changing code.
First inspect existing files; do not overwrite working code without reason.
For each phase, state the plan, implement it, run tests, and summarize changes.
Use safe defaults when requirements are clear; document assumptions.
Ask for clarification only when no safe bounded interpretation exists.
Never report success without executing the relevant validation or test.
Update PROGRESS.md with completed items, test results, decisions, and next step.
Keep the prototype focused, auditable, evidence-based, and demo-ready.