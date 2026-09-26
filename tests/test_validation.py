import pandas as pd

from src.data.validation import validate_dataframe


def test_pass_on_clean_data(sample_df):
    report = validate_dataframe(sample_df)
    assert report.status == "pass"


def test_block_on_missing_required_column(sample_df):
    bad_df = sample_df.drop(columns=["target_value"])
    report = validate_dataframe(bad_df)
    assert report.status == "block"
    assert any(f.check == "required_columns" for f in report.findings)


def test_block_on_missing_values(sample_df):
    bad_df = sample_df.copy()
    bad_df.loc[0, "sales_value"] = None
    report = validate_dataframe(bad_df)
    assert report.status == "block"
    assert any(f.check == "completeness" for f in report.findings)


def test_warning_on_duplicates(sample_df):
    dup_df = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    report = validate_dataframe(dup_df)
    assert report.status in ("warning", "block")
    assert any(f.check == "duplicates" for f in report.findings)


def test_block_on_non_numeric_sales_value(sample_df):
    bad_df = sample_df.copy()
    bad_df["sales_value"] = bad_df["sales_value"].astype(object)
    bad_df.loc[0, "sales_value"] = "not_a_number"
    report = validate_dataframe(bad_df)
    assert report.status == "block"
    assert any(f.check == "numeric_type" for f in report.findings)
