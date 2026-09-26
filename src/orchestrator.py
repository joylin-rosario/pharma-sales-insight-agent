"""SalesInsightSupervisor (CLAUDE.md section 13).

Understands the question, plans, delegates to specialized agents, invokes
skills, verifies guardrails/evidence, and persists state after every
material step. Retries once on recoverable failure; stops and surfaces the
error on repeated/unsafe failure.
"""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from src.agents import governance_agent, insight_agent, sales_analytics_agent
from src.analytics.evidence import to_evidence
from src.nlp.intent_parser import parse_question
from src.observability.tracer import log_event
from src.state.models import (
    AgentTask,
    FinalOutput,
    GuardrailResult,
    PlanStep,
    WorkflowState,
)
from src.state.persistence import save_state


def _scope_label(filters: dict[str, Any]) -> str:
    for level in ["hr_id", "territory", "district", "area", "business_unit"]:
        if filters.get(level):
            return f"{filters[level]} ({level})"
    return "Enterprise"


def run_request(
    df: pd.DataFrame,
    question: str,
    filters: dict[str, Any],
    user_role: str,
    authorized_scope: dict[str, Any],
    dataset_version: str,
    period: Optional[str] = None,
) -> WorkflowState:
    state = WorkflowState(
        user_role=user_role,
        authorized_scope=authorized_scope,
        original_question=question,
        selected_filters=filters,
        dataset_version=dataset_version,
    )
    log_event(state.request_id, "understand", "ok", input_reference="question")

    # 1. Understand -> parsed intent
    state.parsed_intent = parse_question(question)
    save_state(state)

    # 2. Plan
    state.plan = [
        PlanStep(
            task="Run governance input checks",
            agent="GovernanceAgent",
            input_ref="question+filters",
            expected_output="guardrail_results",
        ),
        PlanStep(
            task="Calculate KPIs for requested scope",
            agent="SalesAnalyticsAgent",
            skill="calculate-sales-kpis",
            input_ref="dataframe+filters",
            expected_output="metrics",
        ),
        PlanStep(
            task="Generate insight from verified metrics",
            agent="InsightAgent",
            skill="generate-executive-summary",
            input_ref="metrics",
            expected_output="final_output",
        ),
        PlanStep(
            task="Verify evidence coverage",
            agent="GovernanceAgent",
            input_ref="evidence",
            expected_output="guardrail_results",
        ),
    ]
    log_event(state.request_id, "plan", "ok", output_reference=f"{len(state.plan)}_steps")
    save_state(state)

    # 3. Delegate: Governance input checks
    step = state.plan[0]
    step.status = "running"
    task = AgentTask(agent="GovernanceAgent", step_id=step.step_id, status="running")
    state.agent_tasks.append(task)
    with_error = None
    try:
        input_guardrails: list[GuardrailResult] = governance_agent.run_input_checks(
            question, filters, authorized_scope
        )
        state.guardrail_results.extend(input_guardrails)
        blocking = [g for g in input_guardrails if not g.passed]
        task.status = "done"
        step.status = "done"
        log_event(state.request_id, "guardrail_check", "ok", agent="GovernanceAgent")
    except Exception as exc:  # recoverable-failure path
        task.status = "failed"
        task.error = str(exc)
        step.status = "failed"
        state.errors.append(f"GovernanceAgent input check failed: {exc}")
        log_event(state.request_id, "guardrail_check", "error", agent="GovernanceAgent", error_type=type(exc).__name__)
        blocking = [GuardrailResult(check="governance_agent", passed=False, reason=str(exc))]
    save_state(state)

    if blocking:
        state.final_output = FinalOutput(
            facts=[],
            observations=[],
            hypotheses=[],
            recommendations=[],
            limitations=[b.reason or "Blocked by governance guardrail." for b in blocking],
            evidence_ids=[],
        )
        log_event(state.request_id, "complete", "blocked", agent="GovernanceAgent")
        save_state(state)
        return state

    if not state.parsed_intent.supported:
        state.final_output = FinalOutput(
            limitations=[state.parsed_intent.reason or "Unsupported question."],
        )
        log_event(state.request_id, "complete", "unsupported_intent")
        save_state(state)
        return state

    # 4. Delegate: Sales Analytics Agent (KPIs)
    step = state.plan[1]
    step.status = "running"
    task = AgentTask(agent="SalesAnalyticsAgent", step_id=step.step_id, status="running")
    state.agent_tasks.append(task)
    try:
        summary = sales_analytics_agent.run_summary(df, filters, period)
        task.status = "done"
        step.status = "done"
        log_event(state.request_id, "delegate", "ok", agent="SalesAnalyticsAgent", skill="calculate-sales-kpis",
                   output_reference=f"{len(summary)}_metrics")
    except Exception as exc:
        task.status = "failed"
        task.error = str(exc)
        step.status = "failed"
        state.errors.append(f"SalesAnalyticsAgent failed: {exc}")
        log_event(state.request_id, "delegate", "error", agent="SalesAnalyticsAgent", error_type=type(exc).__name__)
        state.final_output = FinalOutput(limitations=[f"Analytics step failed: {exc}"])
        save_state(state)
        return state
    save_state(state)

    state.metrics = {k: v.model_dump() for k, v in summary.items()}
    state.evidence = [to_evidence(v) for v in summary.values()]

    # 5. Delegate: Insight Agent
    step = state.plan[2]
    step.status = "running"
    task = AgentTask(agent="InsightAgent", step_id=step.step_id, status="running")
    state.agent_tasks.append(task)
    try:
        scope_label = _scope_label(filters)
        insight = insight_agent.run(summary, scope_label, period)
        task.status = "done"
        step.status = "done"
        log_event(state.request_id, "delegate", "ok", agent="InsightAgent", skill="generate-executive-summary")
    except Exception as exc:
        task.status = "failed"
        task.error = str(exc)
        step.status = "failed"
        state.errors.append(f"InsightAgent failed: {exc}")
        log_event(state.request_id, "delegate", "error", agent="InsightAgent", error_type=type(exc).__name__)
        state.final_output = FinalOutput(limitations=[f"Insight step failed: {exc}"])
        save_state(state)
        return state
    save_state(state)

    # 6. Verify: evidence coverage guardrail
    step = state.plan[3]
    step.status = "running"
    evidence_ids = [e.evidence_id for e in state.evidence]
    output_checks = governance_agent.run_output_checks(evidence_ids)
    state.guardrail_results.extend(output_checks)
    step.status = "done"
    log_event(state.request_id, "verify", "ok", agent="GovernanceAgent")

    state.final_output = FinalOutput(
        facts=insight["facts"],
        observations=insight["observations"],
        hypotheses=insight["hypotheses"],
        recommendations=insight["recommendations"],
        limitations=insight["limitations"],
        evidence_ids=evidence_ids,
    )
    log_event(state.request_id, "complete", "ok")
    save_state(state)
    return state
