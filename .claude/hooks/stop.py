#!/usr/bin/env python3
"""Stop hook: run targeted tests and check for unresolved errors.

Informational only — never blocks the session from stopping, since a full
test run may not be relevant to every turn. Prints a warning to stderr if
the fast KPI/guardrail subset fails, so failures are visible but not
disruptive (CLAUDE.md section 16).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    venv_python = ROOT.parent / "venv" / "bin" / "python3"
    python_bin = str(venv_python) if venv_python.exists() else sys.executable
    try:
        result = subprocess.run(
            [python_bin, "-m", "pytest", "tests/test_kpi.py", "tests/test_guardrails.py", "-q"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:
        print(f"[stop] could not run targeted tests (ignored): {exc}", file=sys.stderr)
        return 0

    if result.returncode != 0:
        print("[stop] targeted tests failed — review before considering this phase complete:", file=sys.stderr)
        print(result.stdout[-2000:], file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[stop] hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
