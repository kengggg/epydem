from __future__ import annotations

import pandas as pd

import epydem


def test_summary_markdown_smoke():
    df = pd.DataFrame(
        {
            "onset_date": ["2024-01-01", "2024-01-02", None],
            "age": [10, 20, None],
            "sex": ["M", "F", "F"],
        }
    )

    md = epydem.summary_markdown(
        df,
        by=["sex"],
        date_cols=["onset_date"],
        numeric_cols=["age"],
        categorical_cols=["sex"],
        top_k=2,
    )

    assert "|" in md
    assert "onset_date.min" in md
    assert "age.mean" in md
