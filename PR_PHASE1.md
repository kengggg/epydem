Implements CDC/MMWR epidemiological weeks as the default epiweek logic.

Key points
- Add `mmwr_week(date)` returning `(mmwr_year, mmwr_week)`.
- Add `mmwr_week1_start(year)` (Sunday on/before Jan 4).
- Add `parse_ymd()` to accept `YYYY-MM-DD` strings, `date`, or `datetime`.
- Keep `calculate()` as backward-compatible wrapper returning week number only.
- Replace prior week-0-based tests with focused MMWR boundary tests.

Notes
- This removes the old ISO-like "first Thursday" implementation and eliminates week 0 for MMWR logic.
