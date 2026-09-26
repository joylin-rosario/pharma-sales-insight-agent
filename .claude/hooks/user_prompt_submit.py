#!/usr/bin/env python3
"""UserPromptSubmit hook: flag prohibited intent and prompt-injection patterns.

Reads the Claude Code hook JSON payload from stdin (expects a "prompt" field).
This is a development-time safety net for prompts given to Claude Code itself
while building this project; the app's own GovernanceAgent (src/governance)
is the authoritative runtime guardrail for end-user questions.

Fails safe: any error here prints a warning and allows the prompt through
(exit 0) rather than blocking development.
"""
import json
import sys
from pathlib import Path


def load_patterns() -> dict:
    root = Path(__file__).resolve().parents[2]
    config_path = root / "config" / "guardrails.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text())


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    prompt = str(payload.get("prompt", "")).lower()
    if not prompt:
        return 0

    patterns = load_patterns()
    flagged = []
    for category in (
        "prohibited_employee_decision_keywords",
        "prohibited_employee_inference_keywords",
        "medical_clinical_keywords",
        "pii_phi_keywords",
        "prompt_injection_patterns",
    ):
        for kw in patterns.get(category, []):
            if kw.lower() in prompt:
                flagged.append((category, kw))

    if flagged:
        reasons = "; ".join(f"{cat}:{kw}" for cat, kw in flagged)
        print(
            f"[user_prompt_submit] warning: prompt matches guarded keywords ({reasons}). "
            "Review against CLAUDE.md section 6 before proceeding.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail safe
        print(f"[user_prompt_submit] hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
