import pytest
from datetime import datetime
import epydem
from epydem.epiweek import _verify_date_str


class TestCalculate:
    """Test cases for the calculate function."""

    def test_basic_calculation(self):
        """Test basic epidemiological week calculation."""
        # 2024: January 1st is Monday, first Thursday is January 4th
        # Week 1 starts on Sunday December 31st, 2023
        assert epydem.calculate('2024-01-01') == 1
        assert epydem.calculate('2024-01-04') == 1  # First Thursday
        assert epydem.calculate('2024-01-07') == 1  # First Sunday
        assert epydem.calculate('2024-01-08') == 2  # Second Monday

    def test_week_boundaries(self):
        """Test week boundary calculations."""
        # Test various days within the same week
        assert epydem.calculate('2024-01-01') == 1  # Monday
        assert epydem.calculate('2024-01-02') == 1  # Tuesday
        assert epydem.calculate('2024-01-03') == 1  # Wednesday
        assert epydem.calculate('2024-01-04') == 1  # Thursday
        assert epydem.calculate('2024-01-05') == 1  # Friday
        assert epydem.calculate('2024-01-06') == 1  # Saturday
        assert epydem.calculate('2024-01-07') == 1  # Sunday

    def test_different_years(self):
        """Test calculations for different years."""
        # Test different year scenarios
        assert epydem.calculate('2023-01-01') == 0  # 2023: Jan 1st is Sunday, before epi week 1
        assert epydem.calculate('2025-01-01') == 1  # 2025: Jan 1st is Wednesday, in epi week 1
        assert epydem.calculate('2022-01-01') == 0  # 2022: Jan 1st is Saturday, before epi year

    def test_year_end_scenarios(self):
        """Test end of year scenarios."""
        # December dates that might be in the next year's epi week 1
        assert epydem.calculate('2023-12-31') == 52  # Late in 2023's epi year
        
    def test_week_zero_cases(self):
        """Test cases that should return week 0."""
        # Dates before the epidemiological year starts
        assert epydem.calculate('2022-01-01') == 0  # Saturday, before epi year
        assert epydem.calculate('2022-01-02') == 0  # Sunday, week 1 starts Jan 3rd

    def test_mid_year_calculations(self):
        """Test calculations for various dates throughout the year."""
        # Test some mid-year dates
        assert epydem.calculate('2024-06-01') > 20  # Should be in the 20s
        assert epydem.calculate('2024-12-01') > 45  # Should be in the 40s or 50s

    def test_leap_year(self):
        """Test leap year handling."""
        # 2024 is a leap year
        assert epydem.calculate('2024-02-29') > 0  # Should handle leap day
        assert epydem.calculate('2024-03-01') > 0

    def test_consistent_week_progression(self):
        """Test that week numbers progress consistently."""
        # Test a sequence of dates to ensure proper progression
        week1 = epydem.calculate('2024-01-01')
        week2 = epydem.calculate('2024-01-08')
        week3 = epydem.calculate('2024-01-15')
        
        assert week2 == week1 + 1
        assert week3 == week2 + 1


class TestVerifyDateStr:
    """Test cases for date string validation."""

    def test_valid_date_formats(self):
        """Test valid date string formats."""
        # These should not raise exceptions
        epydem.calculate('2024-01-01')
        epydem.calculate('2024-12-31')
        epydem.calculate('2023-02-28')
        epydem.calculate('2024-02-29')  # Leap year

    def test_invalid_date_formats(self):
        """Test invalid date string formats."""
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('24-01-01')  # Wrong year format
            
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('2024-1-1')  # Wrong month/day format
            
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('2024/01/01')  # Wrong separator
            
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('01-01-2024')  # Wrong order
            
        with pytest.raises(ValueError):
            epydem.calculate('2024-01-32')  # Invalid day
            
        with pytest.raises(ValueError):
            epydem.calculate('2024-13-01')  # Invalid month

    def test_invalid_types(self):
        """Test invalid input types."""
        with pytest.raises((AttributeError, TypeError)):
            epydem.calculate(20240101)  # Integer instead of string
            
        with pytest.raises((AttributeError, TypeError)):
            epydem.calculate(None)  # None instead of string

    def test_empty_and_malformed_strings(self):
        """Test empty and malformed strings."""
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('')  # Empty string
            
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('not-a-date')  # Random string
            
        with pytest.raises(ValueError, match="Invalid date format"):
            epydem.calculate('2024-01-01 10:30:00')  # Too much info


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_first_day_scenarios(self):
        """Test first day of year scenarios for different weekdays."""
        # Test years where Jan 1st falls on different weekdays
        test_cases = [
            ('2023-01-01', 0),  # Sunday - before epi week 1
            ('2024-01-01', 1),  # Monday - in epi week 1
            ('2025-01-01', 1),  # Wednesday - in epi week 1
        ]
        
        for date_str, expected_week in test_cases:
            assert epydem.calculate(date_str) == expected_week

    def test_year_transition(self):
        """Test the transition between epidemiological years."""
        # The end of 2023's epi year and start of 2024's
        assert epydem.calculate('2023-12-30') >= 52  # Late in 2023's epi year
        assert epydem.calculate('2023-12-31') == 52   # Late in 2023's epi year
        assert epydem.calculate('2024-01-01') == 1   # Start of 2024's week 1

    def test_maximum_week_numbers(self):
        """Test that week numbers don't exceed expected maximums."""
        # Test various dates to ensure no week number is > 53
        test_dates = [
            '2024-12-31', '2024-12-30', '2024-12-29',
            '2023-12-31', '2023-12-30', '2023-12-29',
            '2025-12-31', '2025-12-30', '2025-12-29'
        ]
        
        for date_str in test_dates:
            week_num = epydem.calculate(date_str)
            assert 0 <= week_num <= 53, f"Week number {week_num} out of range for {date_str}"


class TestPrivateVerifyFunction:
    """Test cases for the private _verify_date_str function."""
    
    def test_verify_valid_formats(self):
        """Test that _verify_date_str accepts valid formats."""
        assert _verify_date_str("2024-01-01") == True
        assert _verify_date_str("2023-12-31") == True
        assert _verify_date_str("2000-02-29") == True  # Leap year
        assert _verify_date_str("1999-01-01") == True
    
    def test_verify_invalid_formats(self):
        """Test that _verify_date_str rejects invalid formats."""
        invalid_formats = [
            "24-01-01",       # Wrong year format
            "2024-1-01",      # Wrong month format  
            "2024-01-1",      # Wrong day format
            "2024/01/01",     # Wrong separator
            "2024-01",        # Missing day
            "01-01-2024",     # Wrong order
            "not-a-date",     # Not a date
            "",               # Empty string
            "2024-01-01T10:30", # With time
        ]
        
        for invalid_date in invalid_formats:
            with pytest.raises(ValueError, match="Invalid date format"):
                _verify_date_str(invalid_date)


class TestSpecificYearScenarios:
    """Test specific year scenarios to ensure accuracy."""
    
    def test_2023_specific_dates(self):
        """Test specific dates for 2023 (Jan 1 is Sunday)."""
        # 2023: Jan 1 is Sunday, first Thursday is Jan 5
        # Week 1 starts on Jan 2 (Monday)
        assert epydem.calculate("2023-01-01") == 0  # Sunday - before epi week 1
        assert epydem.calculate("2023-01-02") == 1  # Monday - week 1 start
        assert epydem.calculate("2023-01-05") == 1  # Thursday of week 1
        assert epydem.calculate("2023-01-08") == 1  # Sunday of week 1
        
    def test_2024_specific_dates(self):
        """Test specific dates for 2024 (Jan 1 is Monday)."""
        # 2024: Jan 1 is Monday, first Thursday is Jan 4
        # Week 1 starts on Dec 31, 2023 (Sunday)
        assert epydem.calculate("2024-01-01") == 1  # Monday of week 1
        assert epydem.calculate("2024-01-04") == 1  # Thursday of week 1
        assert epydem.calculate("2024-01-07") == 1  # Sunday of week 1
        assert epydem.calculate("2024-01-08") == 2  # Monday - week 2 start
        
    def test_2022_specific_dates(self):
        """Test specific dates for 2022 (Jan 1 is Saturday)."""
        # 2022: Jan 1 is Saturday, first Thursday is Jan 6
        # Week 1 starts on Jan 3, 2022 (Monday)
        assert epydem.calculate("2022-01-01") == 0  # Saturday before epi year
        assert epydem.calculate("2022-01-02") == 0  # Sunday before epi year
        assert epydem.calculate("2022-01-03") == 1  # Monday - week 1 start
        assert epydem.calculate("2022-01-06") == 1  # Thursday of week 1
        assert epydem.calculate("2022-01-09") == 1  # Sunday of week 1


class TestComprehensiveValidation:
    """Comprehensive validation tests."""
    
    def test_all_months_valid(self):
        """Test that all months work correctly."""
        months = ["01", "02", "03", "04", "05", "06", 
                 "07", "08", "09", "10", "11", "12"]
        
        for month in months:
            date_str = f"2024-{month}-15"
            result = epydem.calculate(date_str)
            assert 1 <= result <= 53, f"Invalid week {result} for {date_str}"
    
    def test_sequential_days_progression(self):
        """Test that sequential days show proper week progression."""
        # Test a full week transition
        dates_and_expected = [
            ("2024-01-07", 1),  # Sunday of week 1
            ("2024-01-08", 2),  # Monday of week 2  
            ("2024-01-14", 2),  # Sunday of week 2
            ("2024-01-15", 3),  # Monday of week 3
        ]
        
        for date_str, expected_week in dates_and_expected:
            assert epydem.calculate(date_str) == expected_week
    
    def test_different_years_july_first(self):
        """Test July 1st across different years for consistency."""
        years = ["2020", "2021", "2022", "2023", "2024", "2025"]
        
        for year in years:
            date_str = f"{year}-07-01"
            result = epydem.calculate(date_str)
            # July 1st should always be in week 26-28 range
            assert 25 <= result <= 29, f"Week {result} for {date_str} seems out of range"