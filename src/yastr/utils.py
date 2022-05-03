def mark_text(text, lineno, colno, surround=10):
    line_text = text.splitlines()[lineno - 1]
    snippet_start = max(colno - surround, 0)
    snippet_end = min(colno + surround, len(line_text) - 1)

    snippet = line_text[snippet_start:(snippet_end + 1)]
    cursor_pos = colno - snippet_start - 1
    return '\n'.join([snippet, ' ' * cursor_pos + '^'])
