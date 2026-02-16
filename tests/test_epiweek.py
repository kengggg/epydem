from __future__ import annotations

from datetime import date, datetime

import pytest

import epydem


class TestParseYmd:
    def test_accepts_date(self):
        assert epydem.parse_ymd(date(2024, 1, 1)) == date(2024, 1, 1)

    def test_accepts_datetime(self):
        assert epydem.parse_ymd(datetime(2024, 1, 1, 12, 30)) == date(2024, 1, 1)

    def test_accepts_ymd_string(self):
        assert epydem.parse_ymd("2024-01-01") == date(2024, 1, 1)

    def test_rejects_bad_string(self):
        with pytest.raises(ValueError, match=r"Invalid date format"):
            epydem.parse_ymd("2024/01/01")

    def test_rejects_bad_type(self):
        with pytest.raises(TypeError):
            epydem.parse_ymd(20240101)  # type: ignore[arg-type]


class TestEpiweekMmwr:
    def test_week1_contains_jan4(self):
        # MMWR week 1 starts on Sunday on/before Jan 4.
        assert epydem.mmwr_week1_start(2024) == date(2023, 12, 31)
        assert epydem.mmwr_week1_start(2023) == date(2023, 1, 1)
        assert epydem.mmwr_week1_start(2022) == date(2022, 1, 2)

    def test_known_boundaries_tuple_output(self):
        # Early January can belong to previous MMWR year.
        assert epydem.epiweek("2022-01-01") == (2021, 52)
        assert epydem.epiweek("2022-01-02") == (2022, 1)

        # New year transitions.
        assert epydem.epiweek("2023-01-01") == (2023, 1)
        assert epydem.epiweek("2023-12-31") == (2023, 53)

        assert epydem.epiweek("2024-01-01") == (2024, 1)
        assert epydem.epiweek("2024-01-07") == (2024, 2)
        assert epydem.epiweek("2024-12-31") == (2024, 53)

        assert epydem.epiweek("2026-01-01") == (2025, 53)

    def test_week_number_wrapper(self):
        assert epydem.epiweek_number("2024-01-01") == 1
        assert epydem.calculate("2024-01-01") == 1
        assert epydem.calculate("2022-01-01") == 52
