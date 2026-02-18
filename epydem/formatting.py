from __future__ import annotations

from collections.abc import Sequence


def to_markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Render a simple GitHub-flavored Markdown table.

    Avoids optional deps like `tabulate`.
    """

    headers = list(headers)
    row_strs = [[str(x) for x in r] for r in rows]

    # Escape pipes minimally.
    def esc(s: str) -> str:
        return s.replace("|", "\\|")

    header_line = "| " + " | ".join(esc(h) for h in headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(esc(c) for c in r) + " |" for r in row_strs]

    return "\n".join([header_line, sep_line, *body_lines])
