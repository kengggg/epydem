# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Epydem is a Python library for epidemiological data analysis, specifically focused on calculating epidemiological week numbers from date strings. The library provides a single main function that converts dates in YYYY-MM-DD format to epidemiological week numbers.

## Development Commands

```bash
# Install the package locally for development
pip install .

# Install from GitHub
pip install git+https://github.com/kengggg/epydem.git

# Build the package
python setup.py build

# Create source distribution
python setup.py sdist
```

## Code Architecture

The library follows a simple, focused architecture:

- **epydem/__init__.py**: Exports the main `calculate` function as the public API
- **epydem/epiweek.py**: Contains the core epidemiological week calculation logic
  - `calculate(date_str)`: Main function that takes YYYY-MM-DD date string and returns epidemiological week number
  - `_verify_date_str(date_str)`: Private helper function for strict date format validation

## Key Implementation Details

- **Date Format**: Strictly enforces YYYY-MM-DD format using regex validation
- **Epidemiological Week Logic**: First epi week starts on Sunday and includes the first Thursday of the year
- **Error Handling**: Raises ValueError with descriptive messages for invalid date formats
- **Return Values**: Returns 0 for dates before the start of the epidemiological year

## Code Conventions

- Private functions are prefixed with underscore (e.g., `_verify_date_str`)
- Comprehensive docstrings following Python conventions with Args, Returns, and Raises sections
- Clean public API exposure through `__init__.py`
- No external dependencies - uses only Python standard library

## Testing Notes

Currently no test framework is configured. When adding tests, follow the existing function naming patterns and ensure coverage of:
- Valid date inputs across different years
- Invalid date format handling
- Edge cases around year boundaries
- Week 0 scenarios