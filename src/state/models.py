"""Pydantic state models shared across the supervisor, agents, and UI.

Mirrors the state object defined in CLAUDE.md section 18. Kept as a single
short-lived object per request; no raw personal data is persisted here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class DataQualityStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    BLOCK = "block"


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ParsedIntent(BaseModel):
    question_type: str
    level: Optional[str] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    metric_hint: Optional[str] = None
    supported: bool = True
    reason: Optional[str] = None


class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: new_id("step"))
    task: str
    agent: str
    skill: Optional[str] = None
    input_ref: str
    expected_output: str
    status: str = "planned"  # planned | running | done | failed | skipped


class AgentTask(BaseModel):
    task_id: str = Field(default_factory=lambda: new_id("task"))
    agent: str
    step_id: str
    status: str = "pending"  # pending | running | done | failed
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None


class ToolCall(BaseModel):
    tool_call_id: str = Field(default_factory=lambda: new_id("tool"))
    tool: str
    step_id: str
    status: str = "ok"
    row_count: Optional[int] = None


class EvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: new_id("ev"))
    metric: str
    filters: dict[str, Any] = Field(default_factory=dict)
    period: Optional[str] = None
    value: Optional[float] = None
    reason: Optional[str] = None


class GuardrailResult(BaseModel):
    check: str
    passed: bool
    reason: Optional[str] = None


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: new_id("appr"))
    action_type: str
    decision: ApprovalDecision = ApprovalDecision.PENDING
    approver: Optional[str] = None
    timestamp: Optional[str] = None
    comment: Optional[str] = None


class FinalOutput(BaseModel):
    facts: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class WorkflowState(BaseModel):
    request_id: str = Field(default_factory=lambda: new_id("req"))
    user_role: str
    authorized_scope: dict[str, Any] = Field(default_factory=dict)
    original_question: Optional[str] = None
    parsed_intent: Optional[ParsedIntent] = None
    plan: list[PlanStep] = Field(default_factory=list)
    selected_filters: dict[str, Any] = Field(default_factory=dict)
    dataset_version: Optional[str] = None
    data_quality_status: Optional[DataQualityStatus] = None
    agent_tasks: list[AgentTask] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    guardrail_results: list[GuardrailResult] = Field(default_factory=list)
    approval_status: list[ApprovalRecord] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    replan_history: list[str] = Field(default_factory=list)
    final_output: Optional[FinalOutput] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
