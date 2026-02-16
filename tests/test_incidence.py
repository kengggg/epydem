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
    # default output is wide
    assert list(out.columns) == ["cases"]

    assert out.loc[pd.to_datetime("2024-01-01").date(), "cases"] == 2
    assert out.loc[pd.to_datetime("2024-01-02").date(), "cases"] == 1


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

    # Wide format: index=(epi_year, epi_week), column(s)=province
    assert out.loc[(2021, 52), "A"] == 2
    assert out.loc[(2022, 1), "A"] == 1

    # Long format remains available
    long = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["province"], output="long")
    assert set(long.columns) == {"province", "epi_year", "epi_week", "cases"}
