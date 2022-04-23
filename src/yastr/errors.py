from functools import singledispatchmethod
from json import JSONDecodeError
from pprint import pformat
from textwrap import indent
from typing import Optional

from marshmallow import ValidationError


def mark_text(text, lineno, colno, surround=10):
    line_text = text.splitlines()[lineno - 1]
    snippet_start = max(colno - surround, 0)
    snippet_end = min(colno + surround, len(line_text) - 1)

    snippet = line_text[snippet_start:(snippet_end + 1)]
    cursor_pos = colno - snippet_start - 1
    return '\n'.join([snippet, ' ' * cursor_pos + '^'])


class ConfigError(RuntimeError):
    def __init__(self, msg: str, details: Optional[str] = None, path=None) -> None:
        super().__init__(msg)
        self.msg = msg
        self.details = details
        self.path = path

    def __str__(self):
        text = self.msg + (f': {self.path}' if self.path else '')
        return '\n'.join([text, indent(self.details, '\t')])

    @singledispatchmethod
    @staticmethod  # Use staticmethod (see: https://bugs.python.org/issue39679)
    def of(ex):
        return ConfigError(str(ex))

    @of.register
    def _(ex: JSONDecodeError, **kwargs):
        return ConfigError(
            f'Invalid JSON syntax at line {ex.lineno} column {ex.colno}',
            mark_text(ex.doc, ex.lineno, ex.colno),
            **kwargs,
        )

    @of.register
    def _(ex: ValidationError, **kwargs):
        return ConfigError(
            'Invalid configuration values',
            pformat(ex.messages),
            **kwargs,
        )
