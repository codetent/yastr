import os
import platform
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

import anyconfig
import pytest
from marshmallow import ValidationError
from marshmallow_dataclass import class_schema

from .errors import ConfigError


def validate_markers(obj):
    if not isinstance(obj, (tuple, list)):
        raise ValidationError(f'Invalid marker collection type', field_name='markers')

    for i, marker_spec in enumerate(obj):
        if isinstance(marker_spec, str):
            continue
        elif isinstance(marker_spec, (tuple, list)):
            if not marker_spec:
                raise ValidationError(f'At least a marker name must be provided for element {i}', field_name='markers')
        else:
            raise ValidationError(f'Invalid marker type for element {i}', field_name='markers')


@dataclass
class TestConfig:
    executable: str
    args: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    name: Optional[str] = None
    skip: bool = False
    markers: List[Union[str, List[str]]] = field(default_factory=list, metadata={'validate': validate_markers})
    scripts: List[str] = field(default_factory=list)

    @property
    def resolved_markers(self) -> List[pytest.Mark]:
        def _resolve(spec):
            if isinstance(spec, str):
                return getattr(pytest.mark, spec)
            else:
                return getattr(pytest.mark, spec[0])(*spec[1:])

        return [_resolve(marker) for marker in self.markers]


TestConfigSchema = class_schema(TestConfig)


def load_config(path):
    try:
        config = anyconfig.load(path, ac_template=True, ac_context={'os': os, 'platform': platform})
        return TestConfigSchema().load(config)
    except Exception as ex:
        raise ConfigError.of(ex)
