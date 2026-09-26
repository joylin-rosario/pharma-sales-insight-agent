"""Governance Agent (CLAUDE.md section 14).

Checks authorization, privacy, unsafe intent, and evidence coverage. Blocks
prohibited employee decisions and unauthorized scope.
"""
from __future__ import annotations

from typing import Any

from src.governance.guardrails import run_all_input_guardrails, check_evidence_coverage
from src.state.models import GuardrailResult


def run_input_checks(question: str, requested_filters: dict[str, Any], authorized_scope: dict[str, Any]) -> list[GuardrailResult]:
    return run_all_input_guardrails(question, requested_filters, authorized_scope)


def run_output_checks(evidence_ids: list[str]) -> list[GuardrailResult]:
    return [check_evidence_coverage(evidence_ids)]
