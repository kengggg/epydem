from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from .formatting import to_markdown_table
from .summary import summary


def summary_markdown(
    df: pd.DataFrame,
    *,
    by: Sequence[str] | None = None,
    date_cols: Sequence[str] | None = None,
    numeric_cols: Sequence[str] | None = None,
    categorical_cols: Sequence[str] | None = None,
    top_k: int = 5,
    max_rows: int = 40,
) -> str:
    """Return a human-readable Markdown report for `summary()`.

    This keeps `summary()` as the raw-data primitive (DataFrame) while providing a
    pretty format for quick sharing.

    The report uses wide output internally and prints the first `max_rows` rows.
    """

    wide = summary(
        df,
        by=by,
        date_cols=date_cols,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        top_k=top_k,
        output="wide",
    )

    # Normalize to a 2D table.
    table = wide.reset_index()
    if len(table) > max_rows:
        table = table.head(max_rows)
        truncated_note = f"\n\n_(truncated to first {max_rows} rows)_"
    else:
        truncated_note = ""

    headers = [str(c) for c in table.columns]
    rows = table.astype("object").fillna("").values.tolist()

    return to_markdown_table(headers, rows) + truncated_note
