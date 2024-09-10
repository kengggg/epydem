import re
from datetime import datetime, timedelta

def calculate(date_str):
  """
  Calculate the epidemiological week number for a given date string.

  This function determines the week number of the year for a given date
  based on epidemiological weeks, where the first epidemiological week
  starts on a Sunday and includes the first Thursday of the year.

  Args:
    date_str (str): The date in 'YYYY-MM-DD' format.

  Returns:
    int: The epidemiological week number. Returns 0 if the date is
    before the start of the epidemiological year.

  Raises:
    ValueError: If the provided date string does not match the 'YYYY-MM-DD' format.
  """
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
  """
  Verify that the date string is in the 'YYYY-MM-DD' format.

  Args:
    date_str (str): The date string to verify.

  Returns:
    bool: True if the date string is in the correct format.

  Raises:
    ValueError: If the date string does not match the 'YYYY-MM-DD' format.
  """
  date_pattern = r'^\d{4}-\d{2}-\d{2}$'  # Pattern for YYYY-MM-DD

  if not re.match(date_pattern, date_str):
    raise ValueError("Invalid date format. Please use YYYY-MM-DD")

  return True