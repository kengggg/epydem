Ack — saw this.

**WHY**
- A pretty-printed report is valuable for DX (quick copy/paste into issues, PRs, notebooks, docs) while keeping `summary()` as the raw-data primitive.
- For inference defaults: aggressive inference can surprise users; we should keep inference minimal and explicit.
- For weighted/population-standardized summaries: powerful but can hide assumptions; we should treat it as a separate feature (Phase 3.x) with explicit inputs.

**WHAT (plan)**
1) Add `summary_markdown(...) -> str` (pretty report) that internally calls `summary(..., output='wide'|'long')` but renders a readable Markdown table **without extra deps**.
2) Keep `summary()` returning DataFrames only (raw DF). Users choose: call `summary()` or `summary_markdown()`.
3) Keep inference minimal (stick to common *_date column heuristic; no aggressive guesses beyond that).
4) Weighted summaries: I’ll add a pros/cons debate in a comment (no implementation in this PR).

**ETA**
- I’ll push code + tests in ~2 hours (with local ruff+pytest green before pushing).
