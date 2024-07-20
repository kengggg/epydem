from datetime import datetime, timedelta

def calculate_epi_week(date_str, year):
  date = datetime.strptime(date_str, '%Y-%m-%d')
  year_start = datetime(year, 1, 1)
  week_start = year_start - timedelta(days=year_start.weekday() + 1)

  # If the date is before the start of the epidemiological year, it's week 0
  if date < week_start:
    return 0
  else:
    return (date - week_start).days // 7
