from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

import pandas as pd

from .time import epiweek


EpiFreq = Literal["D", "W-MMWR"]


@dataclass(frozen=True)
class IncidenceSpec:
    date_col: str = "date"
    freq: EpiFreq = "W-MMWR"
    by: tuple[str, ...] = ()


def incidence(
    df: pd.DataFrame,
    *,
    date_col: str,
    freq: EpiFreq = "W-MMWR",
    by: Sequence[str] | None = None,
    count_col: str = "cases",
) -> pd.DataFrame:
    """Compute incidence counts from a line list.

    Args:
        df: Line list dataframe.
        date_col: Column containing dates. Supports values acceptable to `epydem.time.epiweek`.
        freq:
          - "D": daily counts by calendar date
          - "W-MMWR": weekly counts by CDC/MMWR epiweek (returns epi_year + epi_week)
        by: Optional stratification columns.
        count_col: Name of count column in the output.

    Returns:
        DataFrame with grouping columns + a count column.

    Notes:
    - This function does not (yet) fill missing dates/weeks.
    - Future: add `fill_missing`, `start/end`, rolling, cumulative.
    """

    if by is None:
        by_cols: list[str] = []
    else:
        by_cols = list(by)

    if date_col not in df.columns:
        raise KeyError(f"date_col not found: {date_col}")

    work = df.copy()

    if freq == "D":
        work["_date"] = pd.to_datetime(work[date_col]).dt.date
        group_cols = by_cols + ["_date"]
        out = (
            work.groupby(group_cols, dropna=False)
            .size()
            .rename(count_col)
            .reset_index()
            .rename(columns={"_date": "date"})
        )
        return out

    if freq == "W-MMWR":
        # Compute (epi_year, epi_week) per row using our pure-Python epiweek.
        years: list[int] = []
        weeks: list[int] = []
        for v in work[date_col].tolist():
            y, w = epiweek(v)
            years.append(y)
            weeks.append(w)

        work["epi_year"] = years
        work["epi_week"] = weeks

        group_cols = by_cols + ["epi_year", "epi_week"]
        out = work.groupby(group_cols, dropna=False).size().rename(count_col).reset_index()
        return out

    raise ValueError(f"Unknown freq: {freq}")
