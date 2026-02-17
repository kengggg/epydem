from __future__ import annotations

import pandas as pd

import epydem


def test_incidence_weekly_rolling_and_cumulative():
    df = pd.DataFrame(
        {
            "onset_date": [
                "2024-01-01",  # (2024,1)
                "2024-01-08",  # (2024,2)
                "2024-01-08",
            ],
            "province": ["A", "A", "A"],
        }
    )

    base = epydem.incidence(
        df,
        date_col="onset_date",
        freq="W-MMWR",
        by=["province"],
        fill_missing=True,
    )
    # week1=1, week2=2
    assert base.loc[(2024, 1), "A"] == 1
    assert base.loc[(2024, 2), "A"] == 2

    roll2 = epydem.incidence(
        df,
        date_col="onset_date",
        freq="W-MMWR",
        by=["province"],
        fill_missing=True,
        rolling=2,
        rolling_kind="sum",
    )
    assert roll2.loc[(2024, 1), "A"] == 1
    assert roll2.loc[(2024, 2), "A"] == 3

    cum = epydem.incidence(
        df,
        date_col="onset_date",
        freq="W-MMWR",
        by=["province"],
        fill_missing=True,
        cumulative=True,
    )
    assert cum.loc[(2024, 1), "A"] == 1
    assert cum.loc[(2024, 2), "A"] == 3
