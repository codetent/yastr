import os
import shutil
from functools import cached_property
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, run

from pytest import File, Item, Module, skip
from _pytest.outcomes import Failed

from .config import TestConfig, load_config


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

    @property
    def test_timeout(self):
        return self.test_config.timeout or self.config.getoption('timeout')

    @property
    def nodeid(self) -> str:
        return f'{self.parent.nodeid}::{self.test_config.executable}'

    def reportinfo(self):
        return self.fspath, 0, ''

    def runtest(self):
        if self.test_config.skip:
            skip('Skip by user config')

        cmd = [self.fspath] + self.test_config.args

        test_driver = self.config.getini('test_driver')
        if test_driver:
            cmd = [test_driver] + cmd

        try:
            proc = run(
                cmd,
                env=self.test_env,
                encoding=self.test_config.encoding,
                timeout=self.test_timeout,
                text=True,
                capture_output=True,
                check=True,
            )
        except TimeoutExpired as ex:
            stdout, stderr = ex.stdout, ex.stderr
            raise Failed(f'Executable timed out after {self.test_timeout} second(s)', pytrace=False) from None
        except CalledProcessError as ex:
            stdout, stderr = ex.stdout, ex.stderr
            raise Failed(f'Executable returned code {proc.returncode}', pytrace=False) from None
        except:
            stdout, stderr = '', ''
            raise
        else:
            stdout, stderr = proc.stdout, proc.stderr
        finally:
            self.add_report_section('call', 'stdout', stdout)
            self.add_report_section('call', 'stderr', stderr)


class PythonScript(Module):

    @property
    def nodeid(self) -> str:
        return str(self.path.parent)


class ExecutableFile(File):

    @property
    def test_config(self):
        return TestConfig(executable=self.path.name)

    @property
    def nodeid(self) -> str:
        rel_path = self.path.parent.relative_to(self.session.config.rootpath)
        return rel_path.as_posix()

    def collect(self):
        yield ExecutableItem.from_parent(name=self.name, parent=self)


class TestConfigFile(File):

    @cached_property
    def _fixtureinfo(self):
        return self.session._fixturemanager.getfixtureinfo(self, None, None, False)

    @cached_property
    def test_config(self):
        return load_config(self.path)

    @property
    def nodeid(self) -> str:
        rel_path = self.path.parent.relative_to(self.session.config.rootpath)
        return rel_path.as_posix()

    def collect(self):
        executable_path = self.path.parent / self.test_config.executable
        if not executable_path.exists():
            executable_path = Path(shutil.which(self.test_config.executable))

        if executable_path:
            yield ExecutableItem.from_parent(name=executable_path.name, parent=self, path=executable_path)

        for script in self.test_config.scripts:
            script_path = self.path.parent / script
            yield PythonScript.from_parent(self, path=script_path)


def pytest_addoption(parser):
    parser.addini(
        'config_files',
        type='args',
        default=[
            'test-config.json',
            'test-config.json.j2',
            'test-config.yml',
            'test-config.yml.j2',
            'test-config.yaml',
            'test-config.yaml.j2',
        ],
        help='file names of test config files',
    )
    parser.addini(
        'test_driver',
        type='string',
        default=None,
        help='test driver executable that calls the test executable like <driver> <executable> <args>',
    )
    parser.addoption(
        '--timeout',
        type=float,
        default=None,
        action='store',
        dest='timeout',
        help='default timeout for calling test executables',
    )


def pytest_collect_file(path, parent):
    path = Path(path)
    config_paths = [path.parent / name for name in parent.config.getini('config_files')]
    config_exists = any([path.exists() for path in config_paths])

    if config_exists:
        if path in config_paths:
            return TestConfigFile.from_parent(path=path, parent=parent)
    else:
        return ExecutableFile.from_parent(path=path, parent=parent)
