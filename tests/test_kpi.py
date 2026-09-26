from src.analytics.kpi import (
    achievement_pct,
    actual_sales,
    compute_contribution_breakdown,
    compute_summary,
    contribution_pct,
    growth_pct,
    target_sales,
    variance_to_target,
)


def test_actual_and_target_sales(sample_df):
    assert actual_sales(sample_df) == 22000.0
    assert target_sales(sample_df) == 22000.0


def test_achievement_pct_normal():
    value, reason = achievement_pct(9000, 9000)
    assert value == 100.0
    assert reason is None


def test_achievement_pct_zero_denominator():
    value, reason = achievement_pct(1000, 0)
    assert value is None
    assert "undefined" in reason


def test_variance_to_target():
    assert variance_to_target(1000, 900) == 100
    assert variance_to_target(900, 1000) == -100


def test_growth_pct_normal():
    value, reason = growth_pct(1100, 1000)
    assert value == 10.0
    assert reason is None


def test_growth_pct_zero_prior():
    value, reason = growth_pct(1000, 0)
    assert value is None
    assert "undefined" in reason


def test_growth_pct_missing_prior():
    value, reason = growth_pct(1000, None)
    assert value is None
    assert reason is not None


def test_contribution_pct_zero_parent():
    value, reason = contribution_pct(500, 0)
    assert value is None
    assert "undefined" in reason


def test_contribution_pct_normal():
    value, reason = contribution_pct(500, 2000)
    assert value == 25.0


def test_compute_summary_full_precision_and_display_rounding(sample_df):
    summary = compute_summary(sample_df, {})
    assert summary["actual_sales"].value == 22000.0
    assert summary["achievement_pct"].display.endswith("%")
    assert "N/A" not in summary["achievement_pct"].display


def test_compute_contribution_breakdown_sorted_desc(sample_df):
    breakdown = compute_contribution_breakdown(sample_df, "business_unit", {})
    values = [b.value for b in breakdown]
    assert values == sorted(values, reverse=True)
