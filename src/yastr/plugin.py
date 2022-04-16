import os
from functools import cached_property
from pathlib import Path
from subprocess import run, CalledProcessError

from pytest import Item, File, skip
from _pytest.outcomes import Failed

from .config import TestConfig, load_config


CONFIG_FILE_NAMES = [
    'test-config.json',
    'test-config.json.j2',
    'test-config.json.jinja2',
    'test-config.json.jinja',
]


class ExecutableItem(Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for marker in self.test_config.resolved_markers:
            self.add_marker(marker)

    @property
    def test_config(self) -> TestConfig:
        return self.parent.test_config

    @property
    def test_env(self):
        new_env = os.environ.copy()
        new_env.update(self.test_config.environment)
        return new_env

    def reportinfo(self):
        return self.fspath, 0, ''

    def runtest(self):
        if self.test_config.skip:
            skip('Skip by user config')

        proc = run(
            [self.fspath] + self.test_config.args,
            env=self.test_env,
            capture_output=True,
            text=True,
        )
        
        self.add_report_section('call', 'stdout', proc.stdout)
        self.add_report_section('call', 'stderr', proc.stderr)

        try:
            proc.check_returncode()
        except CalledProcessError as ex:
            raise Failed(str(ex), pytrace=False) from None


class ExecutableFile(File):
    @property
    def test_config(self):
        return TestConfig(executable=self.path)

    @property
    def nodeid(self) -> str:
        return str(self.path)

    def collect(self):
        yield ExecutableItem.from_parent(name=self.name, parent=self)


class TestConfigFile(File):
    @cached_property
    def test_config(self):
        return load_config(self.path)

    @property
    def nodeid(self) -> str:
        name = self.test_config.name or self.test_config.executable
        return str(self.path.parent / name)

    def collect(self):
        executable_path = self.path.parent / self.test_config.executable
        yield ExecutableItem.from_parent(name=executable_path.name, parent=self, path=executable_path)



def pytest_collect_file(path, parent):
    path = Path(path)
    config_paths = [path.parent / name for name in CONFIG_FILE_NAMES]
    config_exists = any([path.exists() for path in config_paths])

    if config_exists:
        if path in config_paths:
            return TestConfigFile.from_parent(path=path, parent=parent)
    else:
        return ExecutableFile.from_parent(path=path, parent=parent)
