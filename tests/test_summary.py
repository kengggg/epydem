"""Tests for epydem.summary()."""

import pandas as pd
import pytest

from epydem import summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _long_val(result: pd.DataFrame, column: str, metric: str) -> str:
    """Extract a single value from long-format summary result."""
    mask = (result["column"] == column) & (result["metric"] == metric)
    rows = result.loc[mask, "value"]
    assert len(rows) == 1, f"Expected 1 row for ({column}, {metric}), got {len(rows)}"
    return rows.iloc[0]


def _long_val_by(result: pd.DataFrame, by_val, column: str, metric: str) -> str:
    """Extract a value from long-format with a single by-column."""
    by_col = [c for c in result.columns if c not in ("column", "metric", "value")][0]
    mask = (
        (result[by_col] == by_val)
        & (result["column"] == column)
        & (result["metric"] == metric)
    )
    rows = result.loc[mask, "value"]
    assert len(rows) == 1
    return rows.iloc[0]


# ---------------------------------------------------------------------------
# 1. Default-only-n behavior
# ---------------------------------------------------------------------------


class TestDefaultOnlyN:
    """When no column lists are specified, only n is returned."""

    def test_no_cols_returns_only_n(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        result = summary(df)
        assert len(result) == 1
        assert result.iloc[0]["column"] == "_n"
        assert result.iloc[0]["metric"] == "n"
        assert result.iloc[0]["value"] == "3"

    def test_no_cols_with_by_returns_n_per_group(self):
        df = pd.DataFrame({"grp": ["A", "A", "B"], "x": [1, 2, 3]})
        result = summary(df, by="grp")
        assert len(result) == 2
        assert set(result["grp"]) == {"A", "B"}
        assert all(result["metric"] == "n")
        assert _long_val_by(result, "A", "_n", "n") == "2"
        assert _long_val_by(result, "B", "_n", "n") == "1"

    def test_empty_lists_same_as_none(self):
        df = pd.DataFrame({"a": [1, 2]})
        result = summary(df, date_cols=[], numeric_cols=[], categorical_cols=[])
        assert len(result) == 1
        assert result.iloc[0]["metric"] == "n"


# ---------------------------------------------------------------------------
# 2. By vs no-by
# ---------------------------------------------------------------------------


class TestByVsNoBy:
    """Verify grouping behavior."""

    def test_no_by_single_group(self):
        df = pd.DataFrame({"age": [10, 20, 30]})
        result = summary(df, numeric_cols=["age"])
        assert "column" in result.columns
        # Should have n row + age metrics
        n_row = result[result["column"] == "_n"]
        assert len(n_row) == 1
        assert n_row.iloc[0]["value"] == "3"

    def test_by_single_column(self):
        df = pd.DataFrame({
            "region": ["N", "N", "S", "S", "S"],
            "cases": [1, 2, 3, 4, 5],
        })
        result = summary(df, by="region", numeric_cols=["cases"])
        regions = result["region"].unique()
        assert set(regions) == {"N", "S"}

        # n per group
        assert _long_val_by(result, "N", "_n", "n") == "2"
        assert _long_val_by(result, "S", "_n", "n") == "3"

    def test_by_multiple_columns(self):
        df = pd.DataFrame({
            "region": ["N", "N", "S", "S"],
            "year": [2020, 2020, 2020, 2021],
            "val": [1, 2, 3, 4],
        })
        result = summary(df, by=["region", "year"], numeric_cols=["val"])
        assert "region" in result.columns
        assert "year" in result.columns


# ---------------------------------------------------------------------------
# 3. Date coercion
# ---------------------------------------------------------------------------


class TestDateCoercion:
    """Date columns: coerce invalid -> NaT, count as missing."""

    def test_valid_dates(self):
        df = pd.DataFrame({"onset": ["2024-01-01", "2024-06-15", "2024-12-31"]})
        result = summary(df, date_cols=["onset"])
        assert _long_val(result, "onset", "missing_n") == "0"
        assert _long_val(result, "onset", "missing_pct") == "0.0"
        assert "2024-01-01" in _long_val(result, "onset", "min")
        assert "2024-12-31" in _long_val(result, "onset", "max")

    def test_invalid_dates_become_missing(self):
        df = pd.DataFrame({"onset": ["2024-01-01", "NOT_A_DATE", None]})
        result = summary(df, date_cols=["onset"])
        # Both None and "NOT_A_DATE" should be missing after coercion
        assert _long_val(result, "onset", "missing_n") == "2"
        assert _long_val(result, "onset", "missing_pct") == "66.67"
        assert "2024-01-01" in _long_val(result, "onset", "min")
        assert "2024-01-01" in _long_val(result, "onset", "max")

    def test_all_invalid_dates(self):
        df = pd.DataFrame({"onset": ["bad", "worse", None]})
        result = summary(df, date_cols=["onset"])
        assert _long_val(result, "onset", "missing_n") == "3"
        assert _long_val(result, "onset", "min") == ""
        assert _long_val(result, "onset", "max") == ""


# ---------------------------------------------------------------------------
# 4. Numeric quartiles
# ---------------------------------------------------------------------------


class TestNumericQuartiles:
    """Numeric columns: count, mean, std, min, p25, median, p75, max."""

    def test_basic_numeric(self):
        df = pd.DataFrame({"age": [10, 20, 30, 40, 50]})
        result = summary(df, numeric_cols=["age"])
        assert _long_val(result, "age", "count") == "5"
        assert _long_val(result, "age", "mean") == "30.0"
        assert _long_val(result, "age", "min") == "10.0"
        assert _long_val(result, "age", "max") == "50.0"
        assert _long_val(result, "age", "median") == "30.0"
        assert float(_long_val(result, "age", "p25")) == 20.0
        assert float(_long_val(result, "age", "p75")) == 40.0

    def test_numeric_with_missing(self):
        df = pd.DataFrame({"age": [10, None, 30]})
        result = summary(df, numeric_cols=["age"])
        assert _long_val(result, "age", "missing_n") == "1"
        assert _long_val(result, "age", "count") == "2"
        assert _long_val(result, "age", "mean") == "20.0"

    def test_numeric_missingness_pct(self):
        df = pd.DataFrame({"age": [None, None, 30, 40]})
        result = summary(df, numeric_cols=["age"])
        assert _long_val(result, "age", "missing_n") == "2"
        assert _long_val(result, "age", "missing_pct") == "50.0"


# ---------------------------------------------------------------------------
# 5. Categorical tie-breaking
# ---------------------------------------------------------------------------


class TestCategoricalTieBreaking:
    """Categorical: top-k with deterministic tie-break (count desc, str asc)."""

    def test_basic_top_k(self):
        df = pd.DataFrame({"dx": ["flu", "flu", "flu", "covid", "covid", "rsv"]})
        result = summary(df, categorical_cols=["dx"])
        assert _long_val(result, "dx", "top_1") == "flu"
        assert _long_val(result, "dx", "top_1_n") == "3"
        assert _long_val(result, "dx", "top_2") == "covid"
        assert _long_val(result, "dx", "top_2_n") == "2"
        assert _long_val(result, "dx", "top_3") == "rsv"
        assert _long_val(result, "dx", "top_3_n") == "1"

    def test_tie_break_alphabetical(self):
        """When counts are equal, break ties by string value ascending."""
        df = pd.DataFrame({"dx": ["beta", "alpha", "beta", "alpha"]})
        result = summary(df, categorical_cols=["dx"])
        # Both have count=2; "alpha" < "beta" alphabetically
        assert _long_val(result, "dx", "top_1") == "alpha"
        assert _long_val(result, "dx", "top_2") == "beta"

    def test_missing_token_na(self):
        """Missing values appear as <NA> in categorical top-k."""
        df = pd.DataFrame({"dx": [None, None, None, "flu", "flu"]})
        result = summary(df, categorical_cols=["dx"])
        assert _long_val(result, "dx", "missing_n") == "3"
        assert _long_val(result, "dx", "top_1") == "<NA>"
        assert _long_val(result, "dx", "top_1_n") == "3"
        assert _long_val(result, "dx", "top_2") == "flu"

    def test_fewer_than_top_k(self):
        """When there are fewer unique values than top_k, extra slots are empty."""
        df = pd.DataFrame({"dx": ["flu", "flu"]})
        result = summary(df, categorical_cols=["dx"], top_k=3)
        assert _long_val(result, "dx", "top_1") == "flu"
        assert _long_val(result, "dx", "top_2") == ""
        assert _long_val(result, "dx", "top_3") == ""

    def test_custom_top_k(self):
        df = pd.DataFrame({"dx": ["a", "a", "b", "b", "c", "d"]})
        result = summary(df, categorical_cols=["dx"], top_k=2)
        # Only top_1 and top_2 should appear
        metrics = result[result["column"] == "dx"]["metric"].tolist()
        assert "top_1" in metrics
        assert "top_2" in metrics
        assert "top_3" not in metrics


# ---------------------------------------------------------------------------
# 6. Long and wide output
# ---------------------------------------------------------------------------


class TestOutputFormats:
    """Verify long (default) and wide output formats."""

    def test_long_schema(self):
        df = pd.DataFrame({"age": [10, 20]})
        result = summary(df, numeric_cols=["age"])
        assert list(result.columns) == ["column", "metric", "value"]

    def test_long_with_by_schema(self):
        df = pd.DataFrame({"grp": ["A", "B"], "age": [10, 20]})
        result = summary(df, by="grp", numeric_cols=["age"])
        assert result.columns[0] == "grp"
        assert list(result.columns[-3:]) == ["column", "metric", "value"]

    def test_wide_output(self):
        df = pd.DataFrame({"age": [10, 20, 30]})
        result = summary(df, numeric_cols=["age"], output="wide")
        # Wide should have metric names as columns
        assert "column" in result.columns
        # Check that at least some metric columns exist
        assert "mean" in result.columns or "count" in result.columns

    def test_wide_with_by(self):
        df = pd.DataFrame({"grp": ["A", "A", "B"], "age": [10, 20, 30]})
        result = summary(df, by="grp", numeric_cols=["age"], output="wide")
        assert "grp" in result.columns
        assert "column" in result.columns
