Adds basic incidence computation from a line list (daily and weekly CDC/MMWR).

Key points
- Add `epydem.incidence(df, date_col=..., freq=...)`.
- Supports:
  - `freq="D"` -> daily counts by calendar date
  - `freq="W-MMWR"` -> weekly counts by CDC/MMWR epiweek (adds epi_year + epi_week)
- Optional stratification via `by=[...]`.

Why this implementation
- Incidence is the most common first step for line-list analysis; we want a minimal, composable primitive.
- Using `epi_year` + `epi_week` avoids ambiguity at year boundaries.
- Returning a tidy DataFrame (group columns + `cases`) makes plotting and further transforms straightforward in pandas.
- We intentionally do not implement missing-week filling, rolling averages, or cumulative sums yet to keep the first API small.

Multi-role debate (differences, not consensus)

Role A — pragmatic developer
- 👍 Likes: minimal API, returns tidy DF, works with `by` strata.
- ⚠️ Concern: performance if we iterate row-by-row for epiweek on large datasets; may need vectorization/caching later.

Role B — architecture
- 👍 Likes: keeps time semantics centralized in `epydem.time` and reuses `epiweek()`.
- ⚠️ Concern: frequency naming: `W-MMWR` is clear but may expand to ISO/WHO; may want a more general `freq="W"` + `system=`.

Role C — developer user (DX)
- 👍 Likes: one-liner to get epicurve-like table.
- ⚠️ Concern: expects convenience features soon (fill missing weeks, ordering, start/end bounds, cumulative) and clear examples in docs.

Points of divergence to revisit later
1) Performance: pure-Python loop vs vectorized epiweek mapping.
2) Output schema: keep tidy long DF vs allow pivot/wide convenience.
3) Feature growth: add `fill_missing`, `cumulative`, `rolling`, and `freq` generalization.
