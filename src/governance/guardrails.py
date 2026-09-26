"""Governance guardrails (CLAUDE.md sections 6, 14, 20).

Checks authorization, unsafe intent, prompt injection, and evidence coverage.
Deterministic keyword-based checks — no LLM call, no ambiguity, fully testable.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.state.models import GuardrailResult

_CONFIG = json.loads(Path("config/guardrails.json").read_text())


def _contains_any(text: str, keywords: list[str]) -> str | None:
    lowered = text.lower()
    for kw in keywords:
        if kw.lower() in lowered:
            return kw
    return None


def check_prohibited_intent(question: str) -> GuardrailResult:
    checks = [
        ("employee_decision", _CONFIG["prohibited_employee_decision_keywords"]),
        ("employee_inference", _CONFIG["prohibited_employee_inference_keywords"]),
        ("medical_clinical", _CONFIG["medical_clinical_keywords"]),
        ("pii_phi", _CONFIG["pii_phi_keywords"]),
        ("source_write", _CONFIG["source_write_keywords"]),
    ]
    for name, keywords in checks:
        hit = _contains_any(question, keywords)
        if hit:
            return GuardrailResult(
                check="prohibited_intent",
                passed=False,
                reason=f"Request matched prohibited category '{name}' (keyword: '{hit}'). "
                f"This system does not support employee decisions, medical advice, PII/PHI, "
                f"or source-system writes.",
            )
    return GuardrailResult(check="prohibited_intent", passed=True)


def check_prompt_injection(question: str) -> GuardrailResult:
    hit = _contains_any(question, _CONFIG["prompt_injection_patterns"])
    if hit:
        return GuardrailResult(
            check="prompt_injection",
            passed=False,
            reason=f"Request contains a likely prompt-injection pattern ('{hit}') and was blocked.",
        )
    return GuardrailResult(check="prompt_injection", passed=True)


def check_authorized_scope(requested_filters: dict[str, Any], authorized_scope: dict[str, Any]) -> GuardrailResult:
    """Block if the requested filters reach outside the user's authorized scope."""
    for level, allowed_values in authorized_scope.items():
        if allowed_values is None:
            continue  # unrestricted at this level
        requested = requested_filters.get(level)
        if requested and requested not in allowed_values:
            return GuardrailResult(
                check="authorized_scope",
                passed=False,
                reason=f"Requested {level}='{requested}' is outside your authorized scope {allowed_values}.",
            )
    return GuardrailResult(check="authorized_scope", passed=True)


def check_hr_level_access(requested_level: str, can_view_hr_level: bool) -> GuardrailResult:
    if requested_level == "hr_id" and not can_view_hr_level:
        return GuardrailResult(
            check="hr_level_access",
            passed=False,
            reason="Your role is not authorized to view Health Representative-level detail.",
        )
    return GuardrailResult(check="hr_level_access", passed=True)


def check_evidence_coverage(evidence_ids: list[str]) -> GuardrailResult:
    if not evidence_ids:
        return GuardrailResult(
            check="evidence_coverage",
            passed=False,
            reason="No verified evidence was produced for this request; stopping rather than guessing.",
        )
    return GuardrailResult(check="evidence_coverage", passed=True)


def check_causation_language(text: str) -> GuardrailResult:
    hit = _contains_any(text, _CONFIG["causation_language_keywords"])
    if hit:
        return GuardrailResult(
            check="causation_language",
            passed=False,
            reason=f"Output text implies causation ('{hit}') from descriptive/correlational sales data.",
        )
    return GuardrailResult(check="causation_language", passed=True)


def run_all_input_guardrails(
    question: str, requested_filters: dict[str, Any], authorized_scope: dict[str, Any]
) -> list[GuardrailResult]:
    return [
        check_prompt_injection(question),
        check_prohibited_intent(question),
        check_authorized_scope(requested_filters, authorized_scope),
    ]
