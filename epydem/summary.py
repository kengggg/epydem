from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import pandas as pd

OutputFormat = Literal["long", "wide"]


@dataclass(frozen=True)
class SummarySpec:
    """Configuration for `summary()`.

    This will likely evolve; keep it minimal.
    """

    by: tuple[str, ...] = ()
    date_cols: tuple[str, ...] = ()
    numeric_cols: tuple[str, ...] = ()
    categorical_cols: tuple[str, ...] = ()


def summary(
    df: pd.DataFrame,
    *,
    by: Sequence[str] | None = None,
    date_cols: Sequence[str] | None = None,
    numeric_cols: Sequence[str] | None = None,
    categorical_cols: Sequence[str] | None = None,
    top_k: int = 5,
    output: OutputFormat = "long",
) -> pd.DataFrame:
    """Descriptive summary statistics for an epidemiological line list.

    The goal is a practical, opinionated summary useful for quick EDA.

    Args:
        df: Input dataframe.
        by: Stratification columns.
        date_cols: Date-like columns to summarize (min/max).
        numeric_cols: Numeric columns to summarize.
        categorical_cols: Categorical columns to summarize (top-k frequency table).
        top_k: Number of top categories to include per categorical column.
        output:
          - "long" (default): tidy rows: group + metric/value
          - "wide": pivoted table with metrics as columns

    Returns:
        DataFrame.

    Notes:
    - Missingness is reported as missing_n and missing_pct.
    - Numeric summaries: count, mean, std, min, p25, median, p75, max.
    """

    by_cols = list(by) if by is not None else []

    date_cols = list(date_cols) if date_cols is not None else []
    numeric_cols = list(numeric_cols) if numeric_cols is not None else []
    categorical_cols = list(categorical_cols) if categorical_cols is not None else []

    # Default heuristic: if user doesn't specify, infer a little.
    if not date_cols:
        for c in df.columns:
            if c.endswith("_date") or c in {"date", "onset_date", "report_date"}:
                date_cols.append(c)

    if not numeric_cols:
        numeric_cols = [c for c in df.select_dtypes(include="number").columns]

    # treat remaining non-numeric, non-by, non-date as categorical if user didn't specify
    if not categorical_cols:
        candidates = [c for c in df.columns if c not in set(by_cols + date_cols + numeric_cols)]
        # avoid very wide free-text columns by default
        categorical_cols = candidates

    work = df.copy()

    if by_cols:
        grouped = work.groupby(by_cols, dropna=False)
    else:
        # single group
        grouped = [((), work)]

    rows: list[dict] = []

    def _add(group_key: tuple, metric: str, value, col: str | None = None):
        row: dict = {}
        for i, b in enumerate(by_cols):
            row[b] = group_key[i] if by_cols else None
        row["column"] = col
        row["metric"] = metric
        row["value"] = value
        rows.append(row)

    for key, g in grouped:
        if not isinstance(key, tuple):
            key = (key,)

        n = len(g)
        _add(key, "n", n, col=None)

        # Missingness per column
        for c in date_cols + numeric_cols + categorical_cols:
            if c not in g.columns:
                continue
            miss_n = int(g[c].isna().sum())
            miss_pct = (miss_n / n * 100.0) if n else 0.0
            _add(key, "missing_n", miss_n, col=c)
            _add(key, "missing_pct", round(miss_pct, 3), col=c)

        # Date min/max
        for c in date_cols:
            if c not in g.columns:
                continue
            s = pd.to_datetime(g[c], errors="coerce")
            if s.notna().any():
                _add(key, "min", s.min().date().isoformat(), col=c)
                _add(key, "max", s.max().date().isoformat(), col=c)
            else:
                _add(key, "min", None, col=c)
                _add(key, "max", None, col=c)

        # Numeric summaries
        for c in numeric_cols:
            if c not in g.columns:
                continue
            s = pd.to_numeric(g[c], errors="coerce")
            s_non = s.dropna()
            if s_non.empty:
                for m in ["count", "mean", "std", "min", "p25", "median", "p75", "max"]:
                    _add(key, m, None, col=c)
                continue

            desc = s_non.describe(percentiles=[0.25, 0.5, 0.75])
            _add(key, "count", int(desc["count"]), col=c)
            _add(key, "mean", float(desc["mean"]), col=c)
            _add(key, "std", float(desc["std"]) if "std" in desc else None, col=c)
            _add(key, "min", float(desc["min"]), col=c)
            _add(key, "p25", float(desc["25%"]), col=c)
            _add(key, "median", float(desc["50%"]), col=c)
            _add(key, "p75", float(desc["75%"]), col=c)
            _add(key, "max", float(desc["max"]), col=c)

        # Categorical top-k
        for c in categorical_cols:
            if c not in g.columns:
                continue
            s = g[c].astype("object")
            vc = s.value_counts(dropna=False)
            for rank, (val, cnt) in enumerate(vc.head(top_k).items(), start=1):
                label = "<NA>" if pd.isna(val) else str(val)
                _add(key, f"top_{rank}", label, col=c)
                _add(key, f"top_{rank}_n", int(cnt), col=c)

    out = pd.DataFrame(rows)

    # If no by, we inserted None; remove those columns.
    if not by_cols and "column" in out.columns:
        out = out.drop(columns=[])

    if output == "long":
        return out

    # wide output: index=by, columns=metric names joined with column.
    idx_cols = by_cols if by_cols else []
    out_wide = out.copy()
    out_wide["metric_key"] = out_wide.apply(
        lambda r: (f"{r['column']}.{r['metric']}" if r["column"] is not None else str(r["metric"])),
        axis=1,
    )

    if idx_cols:
        wide = out_wide.pivot_table(
            index=idx_cols,
            columns="metric_key",
            values="value",
            aggfunc="first",
        )
    else:
        wide = out_wide.set_index("metric_key")[["value"]].T

    return wide
