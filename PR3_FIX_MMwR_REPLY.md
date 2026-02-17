Root cause found for the remaining CI failures: our CDC/MMWR year logic was wrong at the year boundary.

Spec nuance:
- 2023-12-31 is the start of 2024 week 1 (week 1 contains Jan 4).
- Our previous implementation assigned it to (2023, 53), which broke weekly fill_missing ranges and the incidence test.

Fix:
- Updated `mmwr_week()` to choose the unique epi-year such that:
  `week1_start(year) <= d < week1_start(year + 1)`
- Updated epiweek boundary tests accordingly.

Commit: 607b258
