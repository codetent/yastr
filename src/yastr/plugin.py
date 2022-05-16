from __future__ import annotations

import os
import shlex
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, run
from typing import TYPE_CHECKING

from _pytest.outcomes import Failed
from pytest import Item, skip

from .config import TestConfig, load_config
from .fixtures import FixtureRequest

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Tuple

    from _pytest.compat import LEGACY_PATH
    from pytest import Node


class YastrTest(Item):
    """Pytest item for running executables triggered by yastr config files."""

    def __init__(self, path: Path, name: Optional[str] = None, **kwargs: Dict[str, Any]) -> None:
        super().__init__(name=(name or path.name), path=path, **kwargs)
        self.own_markers.extend(self.user_config.resolved_markers)

    @cached_property
    def user_config(self) -> TestConfig:
        """User configuration for test."""
        return load_config(self.path)

    @property
    def test_env(self) -> Dict[str, str]:
        """Environment variables for executing the test."""
        new_env = os.environ.copy()
        new_env.update(self.user_config.environment)
        return new_env

    @property
    def test_timeout(self) -> float:
        """Timeout for executing the test."""
        return self.user_config.timeout or self.config.getoption('timeout')

    @property
    def nodeid(self) -> str:
        folder = self.path.parent.relative_to(self.config.rootpath)
        return f'{folder}::{self.name}'

    def reportinfo(self) -> Tuple[LEGACY_PATH, int, str]:
        return self.fspath, 0, ''

    def runtest(self) -> None:
        """Run executable respecting yastr test config."""
        if self.user_config.skip:
            skip('Skipped by user config')

        cmd = [self.user_config.executable] + self.user_config.args
        test_driver = self.config.getini('test_driver')
        if test_driver:
            cmd = shlex.split(test_driver) + cmd

        fixture_req = FixtureRequest(self)
        fixture_req._execute()

        try:
            proc = run(
                cmd,
                env=self.test_env,
                timeout=self.test_timeout,
                capture_output=True,
                check=True,
            )
        except TimeoutExpired as ex:
            stdout, stderr = ex.stdout, ex.stderr
            raise Failed(f'Executable timed out after {self.test_timeout} second(s)', pytrace=False) from None
        except CalledProcessError as ex:
            stdout, stderr = ex.stdout, ex.stderr
            raise Failed(f'Executable returned code {ex.returncode}', pytrace=False) from None
        except:  # noqa: E722
            stdout, stderr = '', ''
            raise
        else:
            stdout, stderr = proc.stdout, proc.stderr
        finally:
            fixture_req._teardown()

            if stdout is not None:
                stdout = stdout.decode(self.user_config.encoding)
                self.add_report_section('call', 'stdout', stdout)

            if stderr is not None:
                stderr = stderr.decode(self.user_config.encoding)
                self.add_report_section('call', 'stderr', stderr)


def pytest_addoption(parser) -> None:
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


def pytest_collect_file(path: LEGACY_PATH, parent: Node) -> Node:
    is_config = any(fnmatch(path, pattern) for pattern in parent.config.getini('yastr_configs'))
    if is_config:
        return YastrTest.from_parent(path=Path(path), parent=parent)
