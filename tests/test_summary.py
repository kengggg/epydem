from __future__ import annotations

import pandas as pd

import epydem

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _long_metric(df: pd.DataFrame, metric: str, col: str | None = None) -> object:
    """Extract a single metric value from a long-format summary."""
    mask = df["metric"] == metric
    if col is not None:
        mask = mask & (df["column"] == col)
    else:
        mask = mask & df["column"].isna()
    vals = df.loc[mask, "value"]
    assert len(vals) == 1, f"Expected 1 row for metric={metric!r}, col={col!r}, got {len(vals)}"
    return vals.iloc[0]


# ---------------------------------------------------------------------------
# 1. by vs no-by
# ---------------------------------------------------------------------------

class TestByVsNoBy:
    """Verify that stratification (`by`) vs ungrouped works correctly."""

    def test_no_by_returns_single_n(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        out = epydem.summary(df)
        assert len(out) == 1
        assert out.iloc[0]["metric"] == "n"
        assert out.iloc[0]["value"] == 3

    def test_by_returns_n_per_group(self):
        df = pd.DataFrame({"sex": ["M", "F", "F"], "age": [10, 20, 30]})
        out = epydem.summary(df, by=["sex"])
        n_rows = out[out["metric"] == "n"]
        assert len(n_rows) == 2
        m_n = n_rows[n_rows["sex"] == "M"]["value"].iloc[0]
        f_n = n_rows[n_rows["sex"] == "F"]["value"].iloc[0]
        assert m_n == 1
        assert f_n == 2

    def test_by_with_multiple_columns(self):
        df = pd.DataFrame({
            "region": ["A", "A", "B", "B"],
            "sex": ["M", "F", "M", "F"],
            "age": [10, 20, 30, 40],
        })
        out = epydem.summary(df, by=["region", "sex"], numeric_cols=["age"])
        n_rows = out[out["metric"] == "n"]
        assert len(n_rows) == 4  # 2 regions x 2 sexes


# ---------------------------------------------------------------------------
# 2. Default-only-n behavior (conservative defaults)
# ---------------------------------------------------------------------------

class TestDefaultOnlyN:
    """If no column lists are specified, summary returns only n per group."""

    def test_no_cols_specified_returns_only_n(self):
        df = pd.DataFrame({
            "onset_date": ["2024-01-01", "2024-01-02"],
            "age": [10, 20],
            "sex": ["M", "F"],
        })
        out = epydem.summary(df)
        assert len(out) == 1
        assert out.iloc[0]["metric"] == "n"
        assert out.iloc[0]["value"] == 2

    def test_no_cols_with_by_returns_only_n_per_group(self):
        df = pd.DataFrame({
            "onset_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "age": [10, 20, 30],
            "sex": ["M", "F", "F"],
        })
        out = epydem.summary(df, by=["sex"])
        # Should have only n rows, one per group
        assert (out["metric"] == "n").all()
        assert len(out) == 2

    def test_no_auto_inference_of_date_cols(self):
        """Columns named onset_date should NOT be auto-detected."""
        df = pd.DataFrame({
            "onset_date": ["2024-01-01", "2024-01-02"],
            "age": [10, 20],
        })
        out = epydem.summary(df)
        # Should only have n, no date metrics
        assert "onset_date" not in out["column"].dropna().values

    def test_no_auto_inference_of_numeric_cols(self):
        """Numeric columns should NOT be auto-detected."""
        df = pd.DataFrame({"age": [10, 20, 30]})
        out = epydem.summary(df)
        assert "age" not in out["column"].dropna().values


# ---------------------------------------------------------------------------
# 3. Date coercion behavior
# ---------------------------------------------------------------------------

class TestDateCoercion:
    """Date columns should be coerced via pd.to_datetime(..., errors='coerce')."""

    def test_valid_dates(self):
        df = pd.DataFrame({"d": ["2024-01-15", "2024-03-20", "2024-02-10"]})
        out = epydem.summary(df, date_cols=["d"])
        assert _long_metric(out, "min", "d") == "2024-01-15"
        assert _long_metric(out, "max", "d") == "2024-03-20"

    def test_invalid_dates_become_missing(self):
        df = pd.DataFrame({"d": ["2024-01-01", "NOT_A_DATE", None]})
        out = epydem.summary(df, date_cols=["d"])
        # One original None + one coerced invalid = 2 missing
        assert _long_metric(out, "missing_n", "d") == 1  # only original None
        # min/max should come from the valid date only
        assert _long_metric(out, "min", "d") == "2024-01-01"
        assert _long_metric(out, "max", "d") == "2024-01-01"

    def test_all_invalid_dates(self):
        df = pd.DataFrame({"d": ["NOT_A_DATE", "ALSO_BAD"]})
        out = epydem.summary(df, date_cols=["d"])
        assert pd.isna(_long_metric(out, "min", "d"))
        assert pd.isna(_long_metric(out, "max", "d"))

    def test_date_missingness(self):
        df = pd.DataFrame({"d": ["2024-01-01", None, None]})
        out = epydem.summary(df, date_cols=["d"])
        assert _long_metric(out, "missing_n", "d") == 2
        pct = _long_metric(out, "missing_pct", "d")
        assert abs(pct - 66.667) < 0.01


# ---------------------------------------------------------------------------
# 4. Numeric quartiles
# ---------------------------------------------------------------------------

class TestNumericQuartiles:
    """Numeric summaries should include count, mean, std, min, p25, median, p75, max."""

    def test_basic_numeric_stats(self):
        df = pd.DataFrame({"age": [10, 20, 30, 40, 50]})
        out = epydem.summary(df, numeric_cols=["age"])
        assert _long_metric(out, "count", "age") == 5
        assert _long_metric(out, "mean", "age") == 30.0
        assert _long_metric(out, "min", "age") == 10.0
        assert _long_metric(out, "max", "age") == 50.0
        assert _long_metric(out, "median", "age") == 30.0
        assert _long_metric(out, "p25", "age") == 20.0
        assert _long_metric(out, "p75", "age") == 40.0
        # std should be present and numeric
        std_val = _long_metric(out, "std", "age")
        assert std_val is not None
        assert std_val > 0

    def test_numeric_with_missing(self):
        df = pd.DataFrame({"age": [10, 20, None, 40]})
        out = epydem.summary(df, numeric_cols=["age"])
        assert _long_metric(out, "missing_n", "age") == 1
        assert _long_metric(out, "count", "age") == 3

    def test_all_missing_numeric(self):
        df = pd.DataFrame({"age": [None, None, None]})
        out = epydem.summary(df, numeric_cols=["age"])
        assert pd.isna(_long_metric(out, "count", "age"))
        assert pd.isna(_long_metric(out, "mean", "age"))


# ---------------------------------------------------------------------------
# 5. Categorical tie-breaking
# ---------------------------------------------------------------------------

class TestCategoricalTieBreaking:
    """Categorical: count desc, then string(value) asc for ties. Missing -> <NA>."""

    def test_basic_top_k(self):
        df = pd.DataFrame({"color": ["red", "blue", "red", "green", "blue", "red"]})
        out = epydem.summary(df, categorical_cols=["color"])
        assert _long_metric(out, "top_1", "color") == "red"
        assert _long_metric(out, "top_1_n", "color") == 3
        assert _long_metric(out, "top_2", "color") == "blue"
        assert _long_metric(out, "top_2_n", "color") == 2
        assert _long_metric(out, "top_3", "color") == "green"
        assert _long_metric(out, "top_3_n", "color") == 1

    def test_tie_break_alphabetical(self):
        """When counts are equal, sort by string value ascending."""
        df = pd.DataFrame({"x": ["cherry", "apple", "banana", "apple", "banana", "cherry"]})
        out = epydem.summary(df, categorical_cols=["x"])
        # All have count 2 => tie-break alphabetically
        assert _long_metric(out, "top_1", "x") == "apple"
        assert _long_metric(out, "top_2", "x") == "banana"
        assert _long_metric(out, "top_3", "x") == "cherry"

    def test_missing_token(self):
        """Missing values should appear as <NA>."""
        df = pd.DataFrame({"x": [None, None, "a"]})
        out = epydem.summary(df, categorical_cols=["x"])
        assert _long_metric(out, "top_1", "x") == "<NA>"
        assert _long_metric(out, "top_1_n", "x") == 2
        assert _long_metric(out, "top_2", "x") == "a"

    def test_top_k_default_is_3(self):
        """Default top_k should be 3."""
        df = pd.DataFrame({"x": ["a", "b", "c", "d"]})
        out = epydem.summary(df, categorical_cols=["x"])
        cat_metrics = out[(out["column"] == "x") & out["metric"].str.startswith("top_")]
        # top_1, top_1_n, top_2, top_2_n, top_3, top_3_n = 6 rows
        assert len(cat_metrics) == 6
        # top_4 should NOT exist
        assert not (out["metric"] == "top_4").any()

    def test_top_k_custom(self):
        """Custom top_k should limit results."""
        df = pd.DataFrame({"x": ["a", "b", "c"]})
        out = epydem.summary(df, categorical_cols=["x"], top_k=2)
        assert (out["metric"] == "top_2").any()
        assert not (out["metric"] == "top_3").any()


# ---------------------------------------------------------------------------
# 6. Wide output
# ---------------------------------------------------------------------------

class TestWideOutput:
    """Verify wide output pivots correctly."""

    def test_wide_with_by(self):
        df = pd.DataFrame({
            "sex": ["M", "F"],
            "age": [10, 20],
        })
        wide = epydem.summary(df, by=["sex"], numeric_cols=["age"], output="wide")
        assert set(wide.index.tolist()) == {"M", "F"}
        assert any("age.mean" in str(c) for c in wide.columns)

    def test_wide_without_by(self):
        df = pd.DataFrame({"age": [10, 20, 30]})
        wide = epydem.summary(df, numeric_cols=["age"], output="wide")
        # Should be a single-row wide table
        assert wide.shape[0] == 1


# ---------------------------------------------------------------------------
# 7. Missingness edge cases
# ---------------------------------------------------------------------------

class TestMissingness:

    def test_missingness_pct_zero_for_complete_column(self):
        df = pd.DataFrame({"age": [1, 2, 3]})
        out = epydem.summary(df, numeric_cols=["age"])
        assert _long_metric(out, "missing_n", "age") == 0
        assert _long_metric(out, "missing_pct", "age") == 0.0
