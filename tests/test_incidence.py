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


def test_incidence_weekly_mmwr_with_strata_fills_missing():
    # Create a gap: only week 1 has cases for stratum B.
    df = pd.DataFrame(
        {
            "onset_date": [
                "2024-01-01",  # (2024,1)
                "2024-01-01",
                "2024-01-08",  # (2024,2)
            ],
            "province": ["A", "B", "A"],
        }
    )

    out = epydem.incidence(
        df,
        date_col="onset_date",
        freq="W-MMWR",
        by=["province"],
        fill_missing=True,
    )

    # Both strata should have rows for both weeks.
    assert out.loc[(2024, 1), "A"] == 1
    assert out.loc[(2024, 2), "A"] == 1

    assert out.loc[(2024, 1), "B"] == 1
    assert out.loc[(2024, 2), "B"] == 0

    # Long format remains available
    long = epydem.incidence(
        df,
        date_col="onset_date",
        freq="W-MMWR",
        by=["province"],
        output="long",
        fill_missing=True,
    )
    assert set(long.columns) == {"province", "epi_year", "epi_week", "cases"}
