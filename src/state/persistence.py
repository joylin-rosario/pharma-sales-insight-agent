"""SQLite-backed persistence for short-lived workflow state.

Local, read/write for workflow state only (per CLAUDE.md section 11: SQLite
is used for local read-only analytical access and workflow state). No raw
personal data or sensitive prompts are stored; HR names are masked before
persistence via src.observability.mask.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src.state.models import WorkflowState

DB_PATH = Path("data/workflow_state.sqlite")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_state (
            request_id TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL,
            state_json TEXT NOT NULL
        )
        """
    )
    return conn


def save_state(state: WorkflowState) -> None:
    state.touch()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO workflow_state (request_id, updated_at, state_json) VALUES (?, ?, ?) "
            "ON CONFLICT(request_id) DO UPDATE SET updated_at=excluded.updated_at, state_json=excluded.state_json",
            (state.request_id, state.updated_at, state.model_dump_json()),
        )
        conn.commit()
    finally:
        conn.close()


def load_state(request_id: str) -> WorkflowState | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT state_json FROM workflow_state WHERE request_id = ?", (request_id,)
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    return WorkflowState.model_validate(json.loads(row[0]))


def list_request_ids(limit: int = 20) -> list[str]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT request_id FROM workflow_state ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]
