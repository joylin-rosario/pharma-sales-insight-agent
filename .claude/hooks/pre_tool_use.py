#!/usr/bin/env python3
"""PreToolUse hook: block destructive commands, secret access, unapproved
paths, and database writes (CLAUDE.md section 16).

Reads the Claude Code hook JSON payload from stdin: {"tool_name": ..., "tool_input": {...}}.
Exit code 2 blocks the tool call and surfaces stderr as the reason to the assistant;
exit code 0 allows it. Fails safe: any hook error allows the call through.
"""
import json
import re
import sys

DESTRUCTIVE_BASH_PATTERNS = [
    r"\brm\s+-rf\s+/(?!home/labuser/Desktop/Agentic_AI_Project)",
    r"\bgit\s+push\s+--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bDROP\s+TABLE\b",
    r"\bDELETE\s+FROM\s+workflow_state\b",
]

SECRET_PATH_PATTERNS = [
    r"\.env(\.|$)",
    r"credentials\.json",
    r"id_rsa",
    r"\.ssh/",
    r"secrets\.",
]

DB_WRITE_PATTERNS = [
    r"\bINSERT\s+INTO\b",
    r"\bUPDATE\s+\w+\s+SET\b",
    r"\bDROP\b",
    r"\bALTER\s+TABLE\b",
]


def block(reason: str) -> int:
    print(f"[pre_tool_use] BLOCKED: {reason}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))
        for pattern in DESTRUCTIVE_BASH_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return block(f"destructive command pattern matched: {pattern}")
        for pattern in SECRET_PATH_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return block(f"command touches a restricted secret path: {pattern}")
        # Only allow SQLite access that is explicitly read-only in this prototype.
        if "sqlite3" in command.lower():
            for pattern in DB_WRITE_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    return block(
                        "direct SQLite write detected; workflow state must be "
                        "written only via src/state/persistence.py (CLAUDE.md section 17)"
                    )

    for key in ("file_path", "path", "notebook_path"):
        value = str(tool_input.get(key, ""))
        if value:
            for pattern in SECRET_PATH_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    return block(f"path touches a restricted secret path: {value}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail safe: never block on hook malfunction
        print(f"[pre_tool_use] hook error (ignored, allowing): {exc}", file=sys.stderr)
        sys.exit(0)
