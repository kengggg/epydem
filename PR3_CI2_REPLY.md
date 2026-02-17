You're right — CI was still failing (ruff) due to import/style issues in `epydem/incidence.py`.

Fixes pushed:
- Use `Sequence` from `collections.abc` (UP035).
- Sort/organize imports and remove inner imports (I001).

Commit: a4e355c
