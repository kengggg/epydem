"""Descriptive summary statistics for epidemiological DataFrames."""

from __future__ import annotations

from typing import Optional, Union

import pandas as pd


def summary(
    df: pd.DataFrame,
    by: Optional[Union[str, list[str]]] = None,
    date_cols: Optional[list[str]] = None,
    numeric_cols: Optional[list[str]] = None,
    categorical_cols: Optional[list[str]] = None,
    top_k: int = 3,
    output: str = "long",
) -> pd.DataFrame:
    """Compute descriptive summary statistics for an epidemiological DataFrame.

    Args:
        df: Input DataFrame.
        by: Column name(s) to group by. If None, summarise the whole frame.
        date_cols: Date columns to summarise (min, max after coercion).
        numeric_cols: Numeric columns to summarise (count, mean, std, quartiles).
        categorical_cols: Categorical columns to summarise (top-k values).
        top_k: Number of top categories to report (default 3).
        output: ``"long"`` (default) or ``"wide"``.

    Returns:
        A DataFrame with summary statistics in the requested format.

        Long format columns: ``by…``, ``column``, ``metric``, ``value``.
        Wide format: pivoted so metrics become columns, indexed by ``by…`` + ``column``.
    """
    date_cols = date_cols or []
    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []

    if by is None:
        by_cols: list[str] = []
    elif isinstance(by, str):
        by_cols = [by]
    else:
        by_cols = list(by)

    groups = df.groupby(by_cols, sort=True) if by_cols else [(None, df)]

    all_rows: list[dict] = []

    for key, group in groups:
        by_dict = _by_dict(by_cols, key)
        n = len(group)
        all_rows.append({**by_dict, "column": "_n", "metric": "n", "value": str(n)})

        for c in date_cols:
            all_rows.extend(_date_metrics(group, c, by_dict))

        for c in numeric_cols:
            all_rows.extend(_numeric_metrics(group, c, by_dict))

        for c in categorical_cols:
            all_rows.extend(_categorical_metrics(group, c, by_dict, top_k))

    result = pd.DataFrame(all_rows)

    if output == "wide":
        index_cols = by_cols + ["column"]
        result = result.pivot_table(
            index=index_cols, columns="metric", values="value", aggfunc="first",
        ).reset_index()
        result.columns.name = None

    return result


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _by_dict(by_cols: list[str], key) -> dict:
    """Build a dict mapping by-column names to their group key values."""
    if not by_cols:
        return {}
    if len(by_cols) == 1:
        # groupby with a list always yields tuple keys; unpack single-element.
        val = key[0] if isinstance(key, tuple) else key
        return {by_cols[0]: val}
    return dict(zip(by_cols, key))


def _missingness(series: pd.Series) -> tuple[int, float]:
    """Return (missing_n, missing_pct) for a series."""
    missing_n = int(series.isna().sum())
    missing_pct = round(missing_n / len(series) * 100, 2) if len(series) > 0 else 0.0
    return missing_n, missing_pct


def _date_metrics(group: pd.DataFrame, col: str, by_dict: dict) -> list[dict]:
    """Compute date-column metrics: missingness, min, max (post-coercion)."""
    coerced = pd.to_datetime(group[col], errors="coerce")
    missing_n, missing_pct = _missingness(coerced)

    rows = [
        {**by_dict, "column": col, "metric": "missing_n", "value": str(missing_n)},
        {**by_dict, "column": col, "metric": "missing_pct", "value": str(missing_pct)},
    ]
    valid = coerced.dropna()
    if len(valid) > 0:
        rows.append(
            {**by_dict, "column": col, "metric": "min", "value": str(valid.min())}
        )
        rows.append(
            {**by_dict, "column": col, "metric": "max", "value": str(valid.max())}
        )
    else:
        rows.append({**by_dict, "column": col, "metric": "min", "value": ""})
        rows.append({**by_dict, "column": col, "metric": "max", "value": ""})
    return rows


def _numeric_metrics(group: pd.DataFrame, col: str, by_dict: dict) -> list[dict]:
    """Compute numeric-column metrics: missingness and descriptive stats."""
    series = pd.to_numeric(group[col], errors="coerce").astype(float)
    missing_n, missing_pct = _missingness(series)

    rows = [
        {**by_dict, "column": col, "metric": "missing_n", "value": str(missing_n)},
        {**by_dict, "column": col, "metric": "missing_pct", "value": str(missing_pct)},
    ]
    valid = series.dropna()
    if len(valid) > 0:
        std_val = valid.std()
        std_str = "" if pd.isna(std_val) else str(round(std_val, 4))
        rows.extend([
            {**by_dict, "column": col, "metric": "count", "value": str(len(valid))},
            {**by_dict, "column": col, "metric": "mean", "value": str(round(valid.mean(), 4))},
            {**by_dict, "column": col, "metric": "std", "value": std_str},
            {**by_dict, "column": col, "metric": "min", "value": str(valid.min())},
            {**by_dict, "column": col, "metric": "p25", "value": str(valid.quantile(0.25))},
            {**by_dict, "column": col, "metric": "median", "value": str(valid.median())},
            {**by_dict, "column": col, "metric": "p75", "value": str(valid.quantile(0.75))},
            {**by_dict, "column": col, "metric": "max", "value": str(valid.max())},
        ])
    else:
        for m in ("count", "mean", "std", "min", "p25", "median", "p75", "max"):
            rows.append({**by_dict, "column": col, "metric": m, "value": ""})
    return rows


def _categorical_metrics(
    group: pd.DataFrame, col: str, by_dict: dict, top_k: int
) -> list[dict]:
    """Compute categorical-column metrics: missingness and top-k values.

    Deterministic tie-break: count descending, then string(value) ascending.
    Missing values are represented as ``<NA>``.
    """
    series = group[col].copy()
    missing_n, missing_pct = _missingness(series)
    rows = [
        {**by_dict, "column": col, "metric": "missing_n", "value": str(missing_n)},
        {**by_dict, "column": col, "metric": "missing_pct", "value": str(missing_pct)},
    ]

    filled = series.fillna("<NA>")
    counts = filled.value_counts()

    # Deterministic tie-break: count desc, then string(value) asc
    sorted_items = sorted(
        counts.items(), key=lambda x: (-x[1], str(x[0]))
    )

    for rank in range(1, top_k + 1):
        if rank <= len(sorted_items):
            val, cnt = sorted_items[rank - 1]
            rows.append(
                {**by_dict, "column": col, "metric": f"top_{rank}", "value": str(val)}
            )
            rows.append(
                {**by_dict, "column": col, "metric": f"top_{rank}_n", "value": str(cnt)}
            )
        else:
            rows.append(
                {**by_dict, "column": col, "metric": f"top_{rank}", "value": ""}
            )
            rows.append(
                {**by_dict, "column": col, "metric": f"top_{rank}_n", "value": ""}
            )
    return rows
