"""Generate a synthetic pharma sales dataset matching the CLAUDE.md data contract.

Run: python data/synthetic/generate_data.py
Writes data/synthetic/sales_data.csv
"""
from __future__ import annotations

import random
from datetime import date

import pandas as pd

random.seed(42)

HIERARCHY = {
    "North BU": {
        "North Area 1": {
            "District N1-A": ["Territory N1-A-1", "Territory N1-A-2"],
            "District N1-B": ["Territory N1-B-1"],
        },
        "North Area 2": {
            "District N2-A": ["Territory N2-A-1", "Territory N2-A-2"],
        },
    },
    "South BU": {
        "South Area 1": {
            "District S1-A": ["Territory S1-A-1", "Territory S1-A-2"],
        },
        "South Area 2": {
            "District S2-A": ["Territory S2-A-1"],
            "District S2-B": ["Territory S2-B-1", "Territory S2-B-2"],
        },
    },
}

PRODUCTS = [
    ("CardioMax", "Cardiology"),
    ("NeuroCalm", "Neurology"),
    ("PulmoEase", "Respiratory"),
    ("GlucoBalance", "Endocrinology"),
]

FIRST_NAMES = ["Asha", "Ravi", "Meera", "Karan", "Sita", "Vikram", "Lena", "Omar", "Priya", "Tomás"]
LAST_NAMES = ["Sharma", "Iyer", "Khan", "Nair", "Rao", "Fernandes", "Menon", "Verma", "Costa", "Gupta"]

PERIODS = [date(2026, 6, 1), date(2026, 7, 1), date(2026, 8, 1)]


def build_rows() -> list[dict]:
    rows = []
    hr_counter = 1
    hr_lookup: dict[str, tuple[str, str]] = {}

    territory_hr: dict[str, str] = {}
    for bu, areas in HIERARCHY.items():
        for area, districts in areas.items():
            for district, territories in districts.items():
                for territory in territories:
                    hr_id = f"HR{hr_counter:04d}"
                    hr_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                    hr_lookup[hr_id] = (hr_name, territory)
                    territory_hr[territory] = hr_id
                    hr_counter += 1

    prior_sales_cache: dict[tuple, float] = {}

    for period in PERIODS:
        for bu, areas in HIERARCHY.items():
            for area, districts in areas.items():
                for district, territories in districts.items():
                    for territory in territories:
                        hr_id = territory_hr[territory]
                        hr_name, _ = hr_lookup[hr_id]
                        for product, ther_area in PRODUCTS:
                            base = random.uniform(8000, 25000)
                            key = (territory, product)
                            prior = prior_sales_cache.get(key)
                            sales_value = round(base * random.uniform(0.85, 1.25), 2)
                            target_value = round(base * random.uniform(0.95, 1.1), 2)
                            units_sold = int(sales_value / random.uniform(40, 60))
                            rows.append(
                                {
                                    "date": period.isoformat(),
                                    "business_unit": bu,
                                    "area": area,
                                    "district": district,
                                    "territory": territory,
                                    "hr_id": hr_id,
                                    "hr_name": hr_name,
                                    "product": product,
                                    "sales_value": sales_value,
                                    "target_value": target_value,
                                    "prior_period_sales": prior if prior is not None else "",
                                    "units_sold": units_sold,
                                    "therapeutic_area": ther_area,
                                    "data_source": "synthetic_demo_v1",
                                    "refresh_timestamp": period.isoformat(),
                                }
                            )
                            prior_sales_cache[key] = sales_value
    return rows


def main() -> None:
    rows = build_rows()
    df = pd.DataFrame(rows)
    out_path = "data/synthetic/sales_data.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
