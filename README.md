# epydem

`epydem` is a Python library for epidemiological data analysis.

## Status

Early-stage. We are modernizing the project foundation (Python >= 3.10, pyproject.toml, CI) and then will implement **CDC/MMWR epidemiological weeks** and core descriptive epi utilities.

## Installation

From GitHub (temporary until PyPI release):

```bash
pip install git+https://github.com/kengggg/epydem.git
```

For development:

```bash
pip install -e '.[dev]'
```

## Usage

```python
import pandas as pd
import epydem

year, week = epydem.epiweek("2024-01-01")
print(year, week)

week_only = epydem.epiweek_number("2024-01-01")
print(week_only)

# Incidence (line list -> counts)
df = pd.DataFrame({"onset_date": ["2024-01-01", "2024-01-02"], "sex": ["M", "F"]})
weekly = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["sex"], fill_missing=True)
weekly_rolling2 = epydem.transform_incidence(weekly, rolling=2)
weekly_cum = epydem.transform_incidence(weekly, cumulative=True)
```

## Descriptive summary

`summary()` returns a tidy (long-format) DataFrame of descriptive statistics.
`summary_markdown()` wraps it into a pretty Markdown table for quick sharing.

**Conservative defaults** — if you omit all column lists, `summary()` returns only `n` per group (no auto-inference):

```python
import pandas as pd
import epydem

df = pd.DataFrame(
    {
        "onset_date": ["2024-01-01", "2024-01-02", None],
        "age": [10, 20, None],
        "sex": ["M", "F", "F"],
    }
)

# Only n per group (no columns specified)
epydem.summary(df, by=["sex"])

# Full summary: explicitly specify columns you care about
out = epydem.summary(
    df,
    by=["sex"],
    date_cols=["onset_date"],
    numeric_cols=["age"],
    categorical_cols=["sex"],
    top_k=3,  # default; top-k categories per categorical column
)

# Wide output (metrics as columns)
wide = epydem.summary(
    df,
    numeric_cols=["age"],
    output="wide",
)

# Pretty Markdown report
md = epydem.summary_markdown(
    df,
    by=["sex"],
    date_cols=["onset_date"],
    numeric_cols=["age"],
    categorical_cols=["sex"],
)
print(md)
```

## Roadmap (high level)

- CDC/MMWR epiweek (week starts Sunday; week 1 contains Jan 4) ✅ (in progress)
- Incidence / epicurves from line lists (pandas) ✅ (in progress)
- Summary statistics (descriptive epi)
