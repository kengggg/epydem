from __future__ import annotations

import pandas as pd

import epydem


def test_summary_basic_long():
    df = pd.DataFrame(
        {
            "onset_date": ["2024-01-01", "2024-01-02", None],
            "age": [10, 20, None],
            "sex": ["M", "F", "F"],
        }
    )

    out = epydem.summary(
        df,
        by=["sex"],
        date_cols=["onset_date"],
        numeric_cols=["age"],
        categorical_cols=["sex"],
        top_k=2,
    )

    # Expect rows for both strata
    assert set(out["sex"].dropna().unique()) == {"M", "F"}

    # Missingness should be present for onset_date
    assert ((out["column"] == "onset_date") & (out["metric"] == "missing_n")).any()


def test_summary_wide_shape():
    df = pd.DataFrame(
        {
            "onset_date": ["2024-01-01", "2024-01-02"],
            "age": [10, 20],
            "sex": ["M", "F"],
        }
    )

    wide = epydem.summary(
        df,
        by=["sex"],
        date_cols=["onset_date"],
        numeric_cols=["age"],
        categorical_cols=["sex"],
        output="wide",
    )

    # Index should be sex
    assert set(wide.index.tolist()) == {"M", "F"}

    # Should have some expected metric columns
    assert any(c.startswith("age.mean") for c in wide.columns)
    assert any(c.startswith("onset_date.min") for c in wide.columns)
