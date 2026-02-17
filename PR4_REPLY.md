Thanks — agreed. I consolidated the workflows so we only have **one** CI.

What changed in this PR:
- Removed the redundant `.github/workflows/test.yml`.
- Kept `.github/workflows/ci.yml` as the single source of truth.
- CI still tests Python 3.10–3.12 (matches `requires-python >= 3.10`).
- Added a quick import smoke test to CI.

Commit: 1f20664
