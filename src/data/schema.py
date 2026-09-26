"""Data contract for uploaded sales files (CLAUDE.md section 8)."""
from __future__ import annotations

import json
import re
from pathlib import Path

_CONFIG = json.loads(Path("config/kpi_config.json").read_text())

REQUIRED_COLUMNS: list[str] = _CONFIG["required_columns"]
OPTIONAL_COLUMNS: list[str] = _CONFIG["optional_columns"]
NUMERIC_COLUMNS = ["sales_value", "target_value", "prior_period_sales", "units_sold"]


def normalize_header(name: str) -> str:
    """snake_case a column header without touching source values."""
    name = name.strip()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    return name.lower()


def normalize_headers(columns: list[str]) -> list[str]:
    return [normalize_header(c) for c in columns]
