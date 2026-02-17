Phase 2.1: incidence DX improvements (docs + rolling/cumulative)

Key points
- Add optional `cumulative=True` for wide output.
- Add optional `rolling=<int>` for wide output with `rolling_kind` (sum/mean).
- Expand README examples for incidence.

Why this implementation
- These options are common in epi workflows (cumulative incidence, smoothed curves) and improve usability without changing the core incidence semantics.
- Implemented at the wide-output layer so behavior is consistent across strata columns.

Multi-role debate (differences, not consensus)

Role A — pragmatic developer
- 👍 Likes: small API surface change, easy to test, minimal code.
- ⚠️ Concern: rolling/cumulative after pivot means we assume the index ordering fully represents time (true for date and (epi_year, epi_week) sorted).

Role B — architecture
- 👍 Likes: keeps incidence core as counts; transformations are optional flags.
- ⚠️ Concern: feature creep: might prefer a separate `transform_incidence()` pipeline later.

Role C — developer user (DX)
- 👍 Likes: fewer steps in notebooks; one-liners for rolling/cumulative.
- ⚠️ Concern: wants more control (e.g., min_periods, centered rolling, cumulative per-calendar-year vs epi-year).

Points of divergence to revisit later
1) Whether these transforms belong inside `incidence()` long-term.
2) Add `min_periods`, `center`, and `cumulative_by` options.
3) Apply transforms to `output="long"` as well.
