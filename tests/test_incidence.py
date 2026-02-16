from __future__ import annotations

import pandas as pd

import epydem


def test_incidence_daily_basic():
    df = pd.DataFrame(
        {
            "onset_date": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-02",
            ],
            "sex": ["M", "F", "M"],
        }
    )

    out = epydem.incidence(df, date_col="onset_date", freq="D")
    assert set(out.columns) == {"date", "cases"}

    # Two cases on 2024-01-01, one on 2024-01-02
    m = {row["date"]: row["cases"] for _, row in out.iterrows()}
    assert m[pd.to_datetime("2024-01-01").date()] == 2
    assert m[pd.to_datetime("2024-01-02").date()] == 1


def test_incidence_weekly_mmwr_with_strata():
    df = pd.DataFrame(
        {
            "onset_date": [
                # 2022-01-01 is MMWR (2021, 52)
                "2022-01-01",
                "2022-01-01",
                "2022-01-02",  # (2022, 1)
            ],
            "province": ["A", "A", "A"],
        }
    )

    out = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["province"])
    assert set(out.columns) == {"province", "epi_year", "epi_week", "cases"}

    # Should have 2 rows: (2021,52)=2 cases, (2022,1)=1 case
    out_sorted = out.sort_values(["epi_year", "epi_week"]).reset_index(drop=True)

    assert out_sorted.loc[0, "epi_year"] == 2021
    assert out_sorted.loc[0, "epi_week"] == 52
    assert out_sorted.loc[0, "cases"] == 2

    assert out_sorted.loc[1, "epi_year"] == 2022
    assert out_sorted.loc[1, "epi_week"] == 1
    assert out_sorted.loc[1, "cases"] == 1
