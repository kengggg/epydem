# Epydem

`Epydem` is a Python library for calculating epidemiological week numbers from date strings.

## Features

- Calculate epidemiological week numbers from YYYY-MM-DD formatted dates
- Follows standard epidemiological week definition where week 1 starts on the Sunday before the first Thursday of the year
- Returns week numbers 1-53, or 0 for dates before the epidemiological year starts
- Strict date format validation with clear error messages

## Installation

You can install the library using pip:

```bash
pip install git+https://github.com/kengggg/epydem.git
```

## Usage

```python
import epydem

# Calculate epidemiological week for a date
week_number = epydem.calculate('2024-01-01')
print(week_number)  # Output: 1

# Week 1 starts on the Sunday before the first Thursday
week_number = epydem.calculate('2024-01-04')  # First Thursday of 2024
print(week_number)  # Output: 1

# Dates before the epidemiological year return 0
week_number = epydem.calculate('2023-12-31')  # Before 2024's epi year
print(week_number)  # Output: 0
```

## Epidemiological Week Definition

Epidemiological weeks follow the standard definition:

- Week 1 is the first week that contains the first Thursday of the year
- Each epidemiological week starts on Sunday and ends on Saturday
- The epidemiological year may start in the previous calendar year
- Week numbers range from 1-53, with 0 for dates before the epidemiological year begins
