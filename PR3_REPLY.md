Thanks — agreed on DX. I updated `fill_missing=True` to fill **per stratum** (not just overall):

- For `freq="D"`: build full (stratum × date) grid between min/max date, then left-join counts and fill 0.
- For `freq="W-MMWR"`: build full (stratum × (epi_year, epi_week)) grid between min/max observed week, then fill 0.

Tests updated to cover a stratum with a missing week now yielding 0.

Commit: 5ae982e
