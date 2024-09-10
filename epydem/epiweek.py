import re
from datetime import datetime, timedelta

def calculate_epi_week(date_str):
  if _verify_date_str(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    year = date.year

    year_start = datetime(year, 1, 1)
    week_start = year_start - timedelta(days=year_start.weekday() + 1)

    # If the date is before the start of the epidemiological year, it's week 0
    if date < week_start:
      return 0
    else:
      return (date - week_start).days // 7

def _verify_date_str(date_str):
  date_pattern = r'^\d{4}-\d{2}-\d{2}$'  # Pattern for YYYY-MM-DD

  if not re.match(date_pattern, date_str):
    raise ValueError("Invalid date format. Please use YYYY-MM-DD")

  return True