import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2026-08-01", "business_unit": "North BU", "area": "North Area 1",
                "district": "District N1-A", "territory": "Territory N1-A-1", "hr_id": "HR0001",
                "hr_name": "Asha Sharma", "product": "CardioMax", "sales_value": 10000.0,
                "target_value": 9000.0, "prior_period_sales": 8000.0, "units_sold": 200,
            },
            {
                "date": "2026-08-01", "business_unit": "North BU", "area": "North Area 1",
                "district": "District N1-A", "territory": "Territory N1-A-2", "hr_id": "HR0002",
                "hr_name": "Ravi Iyer", "product": "CardioMax", "sales_value": 5000.0,
                "target_value": 6000.0, "prior_period_sales": 5500.0, "units_sold": 100,
            },
            {
                "date": "2026-08-01", "business_unit": "South BU", "area": "South Area 1",
                "district": "District S1-A", "territory": "Territory S1-A-1", "hr_id": "HR0003",
                "hr_name": "Meera Nair", "product": "NeuroCalm", "sales_value": 7000.0,
                "target_value": 7000.0, "prior_period_sales": 0.0, "units_sold": 140,
            },
        ]
    )
