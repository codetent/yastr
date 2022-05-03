# from __future__ import annotations  # Does not work with marshmallow dataclass

import os
import platform
from dataclasses import dataclass, field
from functools import singledispatchmethod
from json import JSONDecodeError
from pathlib import Path
from pprint import pformat
from textwrap import indent
from typing import Any, Dict, List, Optional, Tuple, Union

import anyconfig
import pytest
from marshmallow import ValidationError
from marshmallow_dataclass import class_schema

from .utils import mark_text

MarkerType = str
MarkerArgsType = Tuple[str, List[Any]]
MarkerKwargsType = Tuple[str, Dict[str, Any]]


def validate_markers(obj: Any) -> None:
    """Validate config marker spec."""
    if not isinstance(obj, (tuple, list)):
        raise ValidationError('Invalid marker collection type', field_name='markers')

    for i, marker_spec in enumerate(obj):
        if isinstance(marker_spec, str):
            continue
        elif isinstance(marker_spec, (tuple, list)):
            if len(marker_spec) < 2:
                raise ValidationError(f'Marker name and arguments missing for element {i}', field_name='markers')
        else:
            raise ValidationError(f'Invalid marker type for element {i}', field_name='markers')


class ConfigError(RuntimeError):
    """Error typically raised if test config is invalid."""

    def __init__(self, msg: str, details: Optional[str] = None, path: Path = None) -> None:
        super().__init__(msg)
        self.msg = msg
        self.details = details
        self.path = path

    def __str__(self) -> str:
        text = self.msg + (f': {self.path}' if self.path else '')

        if self.details:
            text += '\n' + indent(self.details, '\t')

        return text

    @singledispatchmethod
    @staticmethod  # Use staticmethod (see: https://bugs.python.org/issue39679)
    def of(ex, **kwargs):
        """Create ConfigError from other Exception."""
        return ConfigError(str(ex), **kwargs)

    @of.register
    def _(ex: JSONDecodeError, **kwargs: Dict[str, Any]):
        return ConfigError(
            f'Invalid JSON syntax at line {ex.lineno} column {ex.colno}',
            mark_text(ex.doc, ex.lineno, ex.colno),
            **kwargs,
        )

    @of.register
    def _(ex: ValidationError, **kwargs: Dict[str, Any]):
        return ConfigError(
            'Invalid configuration values',
            pformat(ex.messages),
            **kwargs,
        )


@dataclass
class TestConfig:
    """User-provided yastr test configuration.

    Attributes:
        executable: Path to executable that shall be called
        args: Arguments that shall be provided to executable
        environment: Environment variables to set
        timeout: Timeout in seconds after which executable is killed
        encoding: Encoding of stdout & stderr of executable
        skip: Manually skip test
        markers: Markers to add to the test.
            <marker>:  Set marker without arguments
            [<marker>, [<arg>, ...]]: Set marker with positional arguments
            [<marker>, {<arg key>: <arg value>, ...}]: Set marker with keyword arguments
        fixtures: Fixtures that shall be requested by test
    """

    executable: str
    args: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[float] = None
    encoding: str = 'utf-8'
    skip: bool = False
    markers: List[Union[MarkerType, MarkerArgsType, MarkerKwargsType]] = field(
        default_factory=list,
        metadata={'validate': validate_markers},
    )
    fixtures: List[str] = field(default_factory=list)

    @property
    def resolved_markers(self) -> List[pytest.Mark]:
        """List of all resolved markers including fixtures."""

        def _resolve(spec):
            if isinstance(spec, str):
                return getattr(pytest.mark, spec)
            else:
                name, args = spec
                marker = getattr(pytest.mark, name)
                if isinstance(args, list):
                    return marker(*args)
                else:
                    return marker(**args)

        marker_specs = self.markers.copy()
        marker_specs.append(['usefixtures', self.fixtures])
        return [_resolve(spec) for spec in marker_specs]


TestConfigSchema = class_schema(TestConfig)


def load_config(path: Path) -> TestConfig:
    """Load test configuration from yaml or json file path."""
    try:
        config = anyconfig.load(path, ac_template=True, ac_context={'os': os, 'platform': platform})
        return TestConfigSchema().load(config)
    except Exception as ex:
        raise ConfigError.of(ex, path=path)
