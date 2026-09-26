#!/usr/bin/env python3
"""PostToolUse hook: log tool, duration, status, and any row/evidence hints
to a development-time JSONL log (CLAUDE.md section 16/21).

This logs Claude Code's own tool usage during development, kept separate
from the app's runtime observability log at data/observability_log.jsonl.
Fails safe: logging errors are printed to stderr and never block.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "dev_tool_log.jsonl"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": payload.get("tool_name"),
        "status": "error" if payload.get("tool_response", {}).get("is_error") else "ok",
    }
    tool_input = payload.get("tool_input", {}) or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "command", "path"):
            if key in tool_input:
                event["input_reference"] = str(tool_input[key])[:200]
                break

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[post_tool_use] hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
