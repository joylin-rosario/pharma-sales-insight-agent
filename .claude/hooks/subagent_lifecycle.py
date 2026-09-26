#!/usr/bin/env python3
"""SubagentStart / SubagentStop hook: record delegation and completion.

Used for both events (CLAUDE.md section 16); the payload's own event type
distinguishes start from stop. Fails safe.
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
        "hook_event": payload.get("hook_event_name", "subagent_lifecycle"),
        "agent": payload.get("agent_name") or payload.get("subagent_type"),
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[subagent_lifecycle] hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
