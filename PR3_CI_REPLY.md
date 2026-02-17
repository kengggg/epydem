Good call — I agree.

I fixed the CI failures on PR#3 before asking you to review:
- Removed unused imports in `epydem/epiweek.py` (ruff F401).
- Modernized typing in `epydem/time.py` (avoid deprecated `typing.Tuple/Union`, use `tuple[...]` and `X | Y`).
- Wrapped a long test line to satisfy line-length.

Commit: 485f610
