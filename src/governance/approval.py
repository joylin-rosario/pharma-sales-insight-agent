"""Human-in-the-loop approval gate (CLAUDE.md section 19).

Required before: exporting/publishing a management report, showing/exporting
HR-level detail, accepting a hierarchy correction, presenting a hypothesis as
accepted fact, or enabling a connector/write action. A rejection returns the
workflow to revision rather than silently completing it.
"""
from __future__ import annotations

from datetime import datetime, timezone

from src.state.models import ApprovalDecision, ApprovalRecord

ACTIONS_REQUIRING_APPROVAL = {
    "export_management_report",
    "view_hr_level_detail",
    "accept_hierarchy_correction",
    "present_hypothesis_as_fact",
    "enable_connector_or_write",
}


def create_pending_approval(action_type: str) -> ApprovalRecord:
    if action_type not in ACTIONS_REQUIRING_APPROVAL:
        raise ValueError(f"Unknown approval action_type: {action_type}")
    return ApprovalRecord(action_type=action_type, decision=ApprovalDecision.PENDING)


def record_decision(
    record: ApprovalRecord, approver: str, decision: ApprovalDecision, comment: str | None = None
) -> ApprovalRecord:
    record.approver = approver
    record.decision = decision
    record.comment = comment
    record.timestamp = datetime.now(timezone.utc).isoformat()
    return record


def is_approved(records: list[ApprovalRecord], action_type: str) -> bool:
    matches = [r for r in records if r.action_type == action_type]
    if not matches:
        return False
    return matches[-1].decision == ApprovalDecision.APPROVED
