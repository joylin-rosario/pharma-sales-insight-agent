import pandas as pd

from src.data.hierarchy import find_ambiguous_mappings, reconciliation_ok


def test_no_ambiguous_mappings(sample_df):
    assert find_ambiguous_mappings(sample_df) == []


def test_detects_ambiguous_child_to_multiple_parents(sample_df):
    bad_df = sample_df.copy()
    # Force the same territory under two different districts.
    bad_df.loc[1, "territory"] = bad_df.loc[0, "territory"]
    bad_df.loc[1, "district"] = "District DIFFERENT"
    issues = find_ambiguous_mappings(bad_df)
    assert any(i.level == "territory" for i in issues)


def test_reconciliation_ok_when_totals_match(sample_df):
    ok, diff_pct = reconciliation_ok(sample_df, "business_unit", "area")
    assert ok is True
    assert diff_pct == 0.0
