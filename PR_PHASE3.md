Phase 3: summary() (descriptive epidemiology)

Key points
- Add `epydem.summary(df, by=..., date_cols=..., numeric_cols=..., categorical_cols=...)`.
- Supports stratified summaries via `by=[...]`.
- Long (tidy) output by default; optional `output="wide"`.

WHY
- After incidence/epicurve, the next most common need is quick descriptive EDA: missingness, date ranges, numeric distributions, and top categories.
- A standardized summary makes notebooks and reports faster and more consistent.

WHAT
- Implemented metrics:
  - group size `n`
  - missingness: `missing_n`, `missing_pct`
  - date columns: `min`, `max`
  - numeric columns: `count`, `mean`, `std`, `min`, `p25`, `median`, `p75`, `max`
  - categorical columns: `top_1..top_k` + `top_#_n`

Multi-role debate (differences, not consensus)

Role A — pragmatic developer
- 👍 Likes: covers 80% EDA quickly; configurable columns; works stratified.
- ⚠️ Concern: output schema can grow; must keep naming stable.

Role B — architecture
- 👍 Likes: explicit outputs; can be extended with typed spec objects later.
- ⚠️ Concern: inference heuristics (auto-detect columns) might be surprising; keep it minimal.

Role C — developer user (DX)
- 👍 Likes: one function for a full “first look” summary.
- ⚠️ Concern: wants better defaults and nicer presentation (markdown tables, formatting), but those can be separate utilities.

Points of divergence to revisit later
1) Whether to provide a pretty-printed report (markdown) vs raw DataFrame only.
2) How aggressive to make column inference defaults.
3) Support for weighted summaries / population-standardized metrics.
