"""Backward-compat module.

Historically this project exposed `epydem.calculate()` from `epydem.epiweek`.
We are moving time-related utilities to `epydem.time`.

Prefer using:
- `epydem.epiweek()` -> (year, week)
- `epydem.epiweek_number()` -> week
"""

from __future__ import annotations

from .time import epiweek, epiweek_number, mmwr_week, mmwr_week1_start, parse_ymd


def calculate(date_str: str) -> int:
    """Compatibility alias for week number only."""

    return epiweek_number(date_str)
