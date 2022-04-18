import json
import os
import platform
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

import pytest
from jinja2 import Environment, FileSystemLoader
from marshmallow import ValidationError
from marshmallow_dataclass import class_schema


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
    loader = FileSystemLoader(searchpath=path.parent)
    env = Environment(loader=loader)

    cfg_template = env.get_template(path.name)
    cfg_text = cfg_template.render({'os': os, 'platform': platform})

    config_dict = json.loads(cfg_text)
    return TestConfigSchema().load(config_dict)
