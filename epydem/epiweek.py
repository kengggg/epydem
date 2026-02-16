from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Tuple, Union

DateLike = Union[str, date, datetime]


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
    """Return the start date (Sunday) of MMWR week 1 for a given calendar year.

    CDC/MMWR definition:
    - Weeks start on Sunday.
    - Week 1 is the week that contains January 4.

    Therefore: week 1 starts on the Sunday on or before Jan 4.
    """

    jan4 = date(year, 1, 4)
    # Python: Monday=0 .. Sunday=6. We need offset back to Sunday.
    days_since_sunday = (jan4.weekday() + 1) % 7
    return jan4 - timedelta(days=days_since_sunday)


def mmwr_week(value: DateLike) -> Tuple[int, int]:
    """Compute CDC/MMWR epidemiological week for a date.

    Returns:
        (mmwr_year, mmwr_week)

    Notes:
    - Weeks start Sunday.
    - Week 1 is the week containing Jan 4.
    - Dates in early January can belong to the previous MMWR year.
    """

    d = parse_ymd(value)

    start_this_year = mmwr_week1_start(d.year)
    if d < start_this_year:
        mmwr_year = d.year - 1
        start = mmwr_week1_start(mmwr_year)
    else:
        mmwr_year = d.year
        start = start_this_year

    week = ((d - start).days // 7) + 1
    return mmwr_year, week


def calculate(date_str: str) -> int:
    """Backward-compatible wrapper.

    Historically, `epydem.calculate()` returned a week number only.
    Going forward, CDC/MMWR weeks are the default. For full fidelity,
    use `mmwr_week()`.
    """

    _year, week = mmwr_week(date_str)
    return week
