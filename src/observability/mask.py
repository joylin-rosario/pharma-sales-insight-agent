"""Masking helpers so Health Representative identifiers never hit logs/traces raw."""
from __future__ import annotations

import hashlib


def mask_hr_name(hr_name: str | None) -> str:
    if not hr_name:
        return ""
    digest = hashlib.sha256(hr_name.encode("utf-8")).hexdigest()[:8]
    return f"HR-{digest}"


def mask_value(value, key: str):
    if key in ("hr_name",):
        return mask_hr_name(str(value))
    return value
