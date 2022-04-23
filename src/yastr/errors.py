from functools import singledispatchmethod
from json import JSONDecodeError
from textwrap import indent

from yaml.parser import ParserError as YamlParseError


def mark_text(text, lineno, colno, surround=10):
    line_text = text.splitlines()[lineno - 1]
    snippet_start = max(colno - surround, 0)
    snippet_end = min(colno + surround, len(line_text) - 1)

    snippet = line_text[snippet_start:(snippet_end + 1)]
    cursor_pos = colno - snippet_start - 1
    return '\n'.join([snippet, ' ' * cursor_pos + '^'])


class ConfigError(RuntimeError):
    @singledispatchmethod
    @staticmethod  # Use staticmethod (see: https://bugs.python.org/issue39679)
    def of(ex):
        return ConfigError(str(ex))

    @of.register
    def _(ex: JSONDecodeError):
        return ConfigError('\n'.join([
            f'Invalid JSON syntax at line {ex.lineno} column {ex.colno}:',
            indent(mark_text(ex.doc, ex.lineno, ex.colno), '\t'),
        ]))
