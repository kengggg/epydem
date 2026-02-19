# Phase 3 requirements: summary() (descriptive epidemiology)

These are the agreed requirements for implementing `epydem.summary()`.

## API
- Add `epydem.summary(df, by=None, date_cols=None, numeric_cols=None, categorical_cols=None, top_k=3, output="long") -> pd.DataFrame`

## Conservative defaults (strict)
- If all three of `date_cols`, `numeric_cols`, `categorical_cols` are None/empty:
  - return a summary with **only** group size `n` (respecting `by`)
  - do **not** infer columns automatically

## Metrics
- `n` per group
- Missingness per specified column:
  - `missing_n`, `missing_pct`
- Date columns:
  - compute `min`, `max` after `pd.to_datetime(..., errors="coerce")`
  - invalid/unparseable dates become missing (NaT)
- Numeric columns:
  - `count`, `mean`, `std`, `min`, `p25`, `median`, `p75`, `max`
- Categorical columns:
  - `top_1..top_k` and `top_#_n`
  - deterministic tie-break: sort by count desc, then string(value) asc (treat missing as a stable token like `<NA>`)

## Output
- Default `output="long"` schema:
  - `by...`, `column`, `metric`, `value`
- Optional `output="wide"`:
  - pivot metrics into columns (index includes `by...` + `column`)

## Tests
- cover no-by vs by
- cover default-only-n behavior
- date coercion behavior
- numeric quartiles
- categorical tie-breaking

## Docs
- add README example(s) for `summary()`
