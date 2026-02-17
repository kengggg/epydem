Ack — taking action now.

**WHY**
- To keep `incidence()` from ballooning, transforms should live in a separate function.

**WHAT**
- Refactored PR#5 to implement Option B:
  - `incidence()` now returns counts only (plus output/fill_missing).
  - New `transform_incidence()` applies rolling/cumulative (and is the home for future `min_periods/center/cumulative_by`).
  - Updated tests + README examples to use `transform_incidence(incidence(...), ...)`.

**ETA**
- CI is running now; once all checks are green I’ll ping you to review.

Commit: f5b4e12
