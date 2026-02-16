from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Literal

DateLike = str | date | datetime
EpiWeekSystem = Literal["mmwr"]

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_ymd(value: DateLike) -> date:
    """Parse a date-like value into a `datetime.date`.

    Supported inputs:
    - `datetime.date`
    - `datetime.datetime` (date portion is used)
    - `str` in YYYY-MM-DD format
    """

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        if not _DATE_PATTERN.match(value):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD")
        return datetime.strptime(value, "%Y-%m-%d").date()

    raise TypeError(f"Unsupported type for date: {type(value)!r}")


def mmwr_week1_start(year: int) -> date:
    """Start date (Sunday) of CDC/MMWR week 1 for the given calendar year.

    CDC/MMWR definition:
    - Weeks start on Sunday.
    - Week 1 is the week that contains January 4.

    Therefore: week 1 starts on the Sunday on or before Jan 4.
    """

    jan4 = date(year, 1, 4)
    # Python weekday: Monday=0 .. Sunday=6. Offset back to Sunday.
    days_since_sunday = (jan4.weekday() + 1) % 7
    return jan4 - timedelta(days=days_since_sunday)


def mmwr_week(value: DateLike) -> tuple[int, int]:
    """Compute CDC/MMWR epidemiological week for a date.

    Returns:
        (mmwr_year, mmwr_week)

    Notes:
    - Weeks start Sunday.
    - Week 1 is the week containing Jan 4.
    - The MMWR year is *not* always the calendar year of the date.
      Example: 2023-12-31 is the start of 2024 week 1.

    Implementation rule:
    - Find the unique `mmwr_year` such that:
        week1_start(mmwr_year) <= d < week1_start(mmwr_year + 1)
    """

    d = parse_ymd(value)

    year = d.year
    start = mmwr_week1_start(year)
    start_next = mmwr_week1_start(year + 1)

    if d < start:
        year -= 1
        start = mmwr_week1_start(year)
    elif d >= start_next:
        year += 1
        start = start_next

    week = ((d - start).days // 7) + 1
    return year, week


def epiweek(value: DateLike, system: EpiWeekSystem = "mmwr") -> tuple[int, int]:
    """Compute epidemiological week.

    Currently supported systems:
    - "mmwr" (CDC/MMWR): week starts Sunday, week 1 contains Jan 4.

    Returns:
        (epi_year, epi_week)

    Rationale for returning a tuple:
    - Epi week numbering crosses calendar-year boundaries.
    - A week number alone is ambiguous without its epidemiological year.
    """

    if system == "mmwr":
        return mmwr_week(value)
    raise ValueError(f"Unknown epiweek system: {system}")


def epiweek_number(value: DateLike, system: EpiWeekSystem = "mmwr") -> int:
    """Convenience wrapper returning week number only."""

    _y, w = epiweek(value, system=system)
    return w
