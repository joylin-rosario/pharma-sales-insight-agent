"""Ingest an approved CSV or XLSX sales file (CLAUDE.md section 4 step 1)."""
from __future__ import annotations

import io

import pandas as pd

from src.data.schema import normalize_headers


class UnsupportedFileTypeError(ValueError):
    pass


def load_sales_file(file_obj, filename: str) -> pd.DataFrame:
    """Load a CSV or XLSX file-like object into a normalized DataFrame.

    Source values are never altered; only headers are normalized to snake_case.
    """
    lower = filename.lower()
    if lower.endswith(".csv"):
        df = pd.read_csv(file_obj)
    elif lower.endswith(".xlsx") or lower.endswith(".xls"):
        df = pd.read_excel(file_obj)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file type for '{filename}'. Use .csv or .xlsx.")

    df.columns = normalize_headers(list(df.columns))
    return df


def dataset_version_from_bytes(data: bytes) -> str:
    """Deterministic short version id so lineage to the uploaded file is preserved."""
    import hashlib

    return hashlib.sha256(data).hexdigest()[:12]
