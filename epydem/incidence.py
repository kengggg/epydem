from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

import pandas as pd

from .time import epiweek


EpiFreq = Literal["D", "W-MMWR"]
OutputFormat = Literal["long", "wide"]


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
    output: OutputFormat = "wide",
    fill_missing: bool = True,
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
        output:
          - "wide" (default): pivot table style (DX-friendly)
          - "long": tidy long-form table
        fill_missing: If True, fill missing dates/weeks with 0 counts.

    Returns:
        DataFrame in the requested output format.

    Notes:
    - Performance: for weekly counts we compute epiweek for *unique* dates and map back,
      avoiding a pure Python loop per row.
    """

    if by is None:
        by_cols: list[str] = []
    else:
        by_cols = list(by)

    if date_col not in df.columns:
        raise KeyError(f"date_col not found: {date_col}")

    work = df.copy()

    if freq == "D":
        work["date"] = pd.to_datetime(work[date_col]).dt.date
        group_cols = by_cols + ["date"]
        long = work.groupby(group_cols, dropna=False).size().rename(count_col).reset_index()

        if fill_missing and by_cols == []:
            # Fill missing calendar dates for the overall series.
            all_dates = pd.date_range(long["date"].min(), long["date"].max(), freq="D").date
            long = (
                long.set_index("date")
                .reindex(all_dates, fill_value=0)
                .rename_axis("date")
                .reset_index()
            )

        if output == "long":
            return long

        # wide
        if by_cols:
            wide = long.pivot_table(
                index="date",
                columns=by_cols,
                values=count_col,
                aggfunc="sum",
                fill_value=0,
            )
        else:
            wide = long.set_index("date")[[count_col]]

        return wide.sort_index()

    if freq == "W-MMWR":
        # Compute (epi_year, epi_week) for unique dates, then map back for performance.
        uniq = pd.unique(work[date_col])
        mapping = {v: epiweek(v) for v in uniq}
        epi_pairs = work[date_col].map(mapping)

        work["epi_year"] = epi_pairs.map(lambda t: t[0])
        work["epi_week"] = epi_pairs.map(lambda t: t[1])

        group_cols = by_cols + ["epi_year", "epi_week"]
        long = work.groupby(group_cols, dropna=False).size().rename(count_col).reset_index()

        if fill_missing and by_cols == []:
            # Fill missing epiweeks between min and max observed.
            long = long.sort_values(["epi_year", "epi_week"]).reset_index(drop=True)
            start_y, start_w = int(long.iloc[0]["epi_year"]), int(long.iloc[0]["epi_week"])
            end_y, end_w = int(long.iloc[-1]["epi_year"]), int(long.iloc[-1]["epi_week"])

            # Build the full sequence of (y,w) by stepping Sundays.
            # We use the canonical week start for MMWR year/week computed via epiweek.
            # (Implementation detail: step 7 days from the first observed week start.)
            from .time import mmwr_week1_start
            from datetime import timedelta

            start_date = mmwr_week1_start(start_y) + timedelta(days=(start_w - 1) * 7)
            end_date = mmwr_week1_start(end_y) + timedelta(days=(end_w - 1) * 7)

            full_pairs = []
            d = start_date
            while d <= end_date:
                full_pairs.append(epiweek(d))
                d += timedelta(days=7)

            idx = pd.MultiIndex.from_tuples(full_pairs, names=["epi_year", "epi_week"])
            long = (
                long.set_index(["epi_year", "epi_week"])
                .reindex(idx, fill_value=0)
                .reset_index()
            )

        if output == "long":
            return long

        # wide
        if by_cols:
            wide = long.pivot_table(
                index=["epi_year", "epi_week"],
                columns=by_cols,
                values=count_col,
                aggfunc="sum",
                fill_value=0,
            )
        else:
            wide = long.set_index(["epi_year", "epi_week"])[[count_col]]

        return wide.sort_index()

    raise ValueError(f"Unknown freq: {freq}")
