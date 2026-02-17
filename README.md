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
import epydem

year, week = epydem.epiweek("2024-01-01")
print(year, week)

week_only = epydem.epiweek_number("2024-01-01")
print(week_only)

# Incidence (line list -> counts)
# df = pandas.DataFrame({"onset_date": [...], "sex": [...]})
# weekly = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["sex"], fill_missing=True)
# weekly_rolling2 = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["sex"], rolling=2)
# weekly_cum = epydem.incidence(df, date_col="onset_date", freq="W-MMWR", by=["sex"], cumulative=True)
```

## Roadmap (high level)

- CDC/MMWR epiweek (week starts Sunday; week 1 contains Jan 4) ✅ (in progress)
- Incidence / epicurves from line lists (pandas) ✅ (in progress)
- Summary statistics (descriptive epi)
