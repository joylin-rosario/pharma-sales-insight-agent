"""Structured JSONL observability events (CLAUDE.md section 21).

Every event shares a request_id so the full trace (section 22) can be
reconstructed for the UI's Trace tab.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOG_PATH = Path("data/observability_log.jsonl")


def log_event(
    request_id: str,
    workflow_step: str,
    status: str,
    agent: Optional[str] = None,
    skill: Optional[str] = None,
    tool: Optional[str] = None,
    latency_ms: Optional[float] = None,
    input_reference: Optional[str] = None,
    output_reference: Optional[str] = None,
    error_type: Optional[str] = None,
    approval_status: Optional[str] = None,
) -> dict[str, Any]:
    event = {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_step": workflow_step,
        "agent": agent,
        "skill": skill,
        "tool": tool,
        "status": status,
        "latency_ms": latency_ms,
        "input_reference": input_reference,
        "output_reference": output_reference,
        "error_type": error_type,
        "approval_status": approval_status,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return event


class StepTimer:
    """Context manager that times a step and writes a single trace event."""

    def __init__(self, request_id: str, workflow_step: str, **kwargs: Any) -> None:
        self.request_id = request_id
        self.workflow_step = workflow_step
        self.kwargs = kwargs
        self._start = 0.0

    def __enter__(self) -> "StepTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        latency_ms = round((time.perf_counter() - self._start) * 1000, 2)
        status = "error" if exc_type else "ok"
        error_type = exc_type.__name__ if exc_type else None
        log_event(
            self.request_id,
            self.workflow_step,
            status=status,
            latency_ms=latency_ms,
            error_type=error_type,
            **self.kwargs,
        )
        return False  # never swallow exceptions


def read_events(request_id: str) -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    events = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if event.get("request_id") == request_id:
                events.append(event)
    return events
