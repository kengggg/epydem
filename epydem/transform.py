from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import pandas as pd

RollingKind = Literal["sum", "mean"]


@dataclass(frozen=True)
class TransformSpec:
    rolling: int | None = None
    rolling_kind: RollingKind = "sum"
    min_periods: int = 1
    center: bool = False
    cumulative: bool = False


def transform_incidence(
    data: pd.DataFrame,
    *,
    rolling: int | None = None,
    rolling_kind: RollingKind = "sum",
    min_periods: int = 1,
    center: bool = False,
    cumulative: bool = False,
    time_cols: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Apply time-series transforms to incidence outputs.

    This is intentionally separate from `incidence()` to keep `incidence()` as a
    stable counts primitive.

    Supported inputs:
    - Wide incidence output: index is time (e.g. date or (epi_year, epi_week)).
    - Long incidence output: requires `time_cols` (or inferred), and transforms
      are applied per non-time column group.

    Args:
        data: Output from `epydem.incidence(...)`.
        rolling: Rolling window size.
        rolling_kind: "sum" or "mean".
        min_periods: Passed to pandas rolling.
        center: Passed to pandas rolling.
        cumulative: If True, apply cumulative sum.
        time_cols: For long-form data, the time columns. If None, we try to infer
            ("date") or ("epi_year", "epi_week").

    Returns:
        Transformed DataFrame with the same shape/schema as input.
    """

    if rolling is None and not cumulative:
        return data

    # Wide: DataFrameIndex is time.
    if time_cols is None and ("date" not in data.columns) and ("epi_year" not in data.columns):
        wide = data.sort_index()
        if rolling is not None:
            r = wide.rolling(window=rolling, min_periods=min_periods, center=center)
            wide = r.sum() if rolling_kind == "sum" else r.mean()
        if cumulative:
            wide = wide.cumsum()
        return wide

    # Long: operate on a value column per group.
    df = data.copy()

    if time_cols is None:
        if "date" in df.columns:
            time_cols = ["date"]
        elif ("epi_year" in df.columns) and ("epi_week" in df.columns):
            time_cols = ["epi_year", "epi_week"]
        else:
            raise ValueError("Cannot infer time_cols for long-form incidence")

    value_cols = [c for c in df.columns if c not in set(time_cols)]
    if len(value_cols) != 1:
        raise ValueError(
            "Long-form incidence must have exactly one value column (e.g., 'cases'). "
            f"Got {value_cols}"
        )
    value_col = value_cols[0]

    group_cols = [c for c in df.columns if c not in set(time_cols + [value_col])]

    df = df.sort_values(list(time_cols))

    def _apply(group: pd.DataFrame) -> pd.DataFrame:
        s = group[value_col]
        if rolling is not None:
            r = s.rolling(window=rolling, min_periods=min_periods, center=center)
            s = r.sum() if rolling_kind == "sum" else r.mean()
        if cumulative:
            s = s.cumsum()
        group[value_col] = s
        return group

    if group_cols:
        out = df.groupby(group_cols, dropna=False, sort=False, group_keys=False).apply(_apply)
    else:
        out = _apply(df)

    return out
