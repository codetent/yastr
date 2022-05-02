import os
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, run

from pytest import Item, skip
from _pytest.outcomes import Failed

from .api.fixtures import FixtureRequest
from .config import TestConfig, load_config


class YastrTest(Item):

    def __init__(self, path, name=None, **kwargs):
        super().__init__(name=(name or path.name), path=path, **kwargs)
        self.own_markers.extend(self.test_config.resolved_markers)

    @cached_property
    def test_config(self) -> TestConfig:
        return load_config(self.path)

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
        folder = self.path.parent.relative_to(self.config.rootpath)
        return f'{folder}::{self.name}'

    def reportinfo(self):
        return self.fspath, 0, ''

    def runtest(self):
        if self.test_config.skip:
            skip('Skip by user config')

        cmd = [self.test_config.executable] + self.test_config.args

        test_driver = self.config.getini('test_driver')
        if test_driver:
            cmd = [test_driver] + cmd

        fixture_req = FixtureRequest(self)
        fixture_req._execute()

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
            fixture_req._teardown()

            self.add_report_section('call', 'stdout', stdout)
            self.add_report_section('call', 'stderr', stderr)


def pytest_addoption(parser):
    parser.addini(
        'yastr_configs',
        type='args',
        default=['*.yastr.*'],
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
    is_config = any(fnmatch(path, pattern) for pattern in parent.config.getini('yastr_configs'))
    if is_config:
        return YastrTest.from_parent(path=Path(path), parent=parent)
