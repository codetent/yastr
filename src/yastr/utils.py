"""Utility functions for different purposes."""


def mark_text(text: str, lineno: int, colno: int, surround: int = 10) -> str:
    """Cut snippet out of given text at given position and set marker."""
    line_text = text.splitlines()[lineno - 1]
    snippet_start = max(colno - surround, 0)
    snippet_end = min(colno + surround, len(line_text) - 1)

    snippet = line_text[snippet_start:(snippet_end + 1)]
    cursor_pos = colno - snippet_start - 1
    return '\n'.join([snippet, ' ' * cursor_pos + '^'])
