GitHub Actions fix: CI was failing on Python 3.9 because epydem now requires Python >= 3.10 (pyproject.toml).

Changes
- Consolidate CI by removing redundant `.github/workflows/test.yml` (keep `ci.yml` as the single CI).
- Ensure CI only tests supported Python versions (>=3.10).
- Install via `pip install -e '.[dev]'` (single source of truth).
- Add a quick import smoke test to CI.

Why this implementation
- Running CI on unsupported Python versions creates noisy failures and slows iteration.
- Keeping workflows consistent reduces maintenance and confusion.

Multi-role debate (differences, not consensus)

Role A — pragmatic developer
- 👍 Likes: CI goes green and matches supported versions; simpler workflow.
- ⚠️ Concern: removes older-Python signal; but we explicitly don’t support <3.10.

Role B — architecture
- 👍 Likes: single tooling stack (ruff) and consistent install path.
- ⚠️ Concern: having both `ci.yml` and `test.yml` is redundant; consider consolidating later.

Role C — developer user (DX)
- 👍 Likes: less CI noise; clearer support policy.
- ⚠️ Concern: if users want older Python, they’ll need a documented support decision.

Points of divergence to revisit later
1) Consolidate workflows (keep one CI file).
2) Add `python-version: 3.13` when ready.
