#!/usr/bin/env python3
"""SessionStart hook: remind the assistant to read CLAUDE.md and PROGRESS.md.

Fails safe: any error here only prints a warning to stderr and exits 0,
never blocks the session from starting.
"""
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [name for name in ("CLAUDE.md", "PROGRESS.md") if not (root / name).exists()]
    if missing:
        print(f"[session_start] note: missing {', '.join(missing)} at project root", file=sys.stderr)
    print("[session_start] Read CLAUDE.md and PROGRESS.md before changing code (CLAUDE.md section 28).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail safe, never block session start
        print(f"[session_start] hook error (ignored): {exc}", file=sys.stderr)
        sys.exit(0)
