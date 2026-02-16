Implements CDC/MMWR epidemiological weeks as the default epiweek logic.

Key points
- Add `mmwr_week(date)` returning `(mmwr_year, mmwr_week)`.
- Add `mmwr_week1_start(year)` (Sunday on/before Jan 4).
- Add `parse_ymd()` to accept `YYYY-MM-DD` strings, `date`, or `datetime`.
- Keep `calculate()` as backward-compatible wrapper returning week number only.
- Replace prior week-0-based tests with focused MMWR boundary tests.

Why this implementation
- CDC/MMWR weeks start on Sunday and Week 1 is defined as the week containing Jan 4. That implies Week 1 starts on the Sunday on/before Jan 4.
- Computing `week1_start(year)` from Jan 4 is a simple, O(1) pure function that avoids tricky edge cases.
- Returning `(mmwr_year, mmwr_week)` is essential because early January dates can belong to the previous MMWR year.
- `parse_ymd()` centralizes date parsing/validation so later features (incidence curves, summaries) can reuse it.

Multi-role debate (differences, not consensus)

Role A — pragmatic developer
- 👍 Likes: pure function, O(1), easy to test; `parse_ymd()` makes downstream code simpler.
- ⚠️ Concern: backward-compat behavior changes for early-January dates (previously could be week 0; now becomes week 52/53). Correct for MMWR but can surprise users.

Role B — architecture
- 👍 Likes: explicit MMWR semantics; returning `(year, week)` avoids ambiguity.
- ⚠️ Concern: module/API organization. Might prefer a `time/` namespace (e.g., `epydem.time.mmwr_week`) if we later add ISO/WHO week systems.

Role C — developer user (DX)
- 👍 Likes: no week 0; tuple output makes grouping across years correct.
- ⚠️ Concern: naming. Users may want `epiweek()` as the default MMWR function and clear docs with boundary examples (e.g., 2022-01-01 -> (2021, 52)).

Points of divergence to revisit later
1) Naming: `mmwr_week()` vs providing a default `epiweek()` alias.
2) Compatibility: keep `calculate()` returning week-only vs switching `calculate()` to tuple (breaking change).
3) Structure: keep in `epiweek.py` vs split into `epydem/time.py` or `epydem/time/` module.
