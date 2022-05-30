# Advanced Features

## Skipping

For development reasons, single test cases can be skipped by setting the `skip` option:

```yaml
skip: True
```

## Timeout

Sometimes, test executables can be stuck or just last very long. In this case it could make sense to set a timeout after which the test should be aborted. After exceeding it, the current executable will be killed and the test runner will proceeed.

It can be enabled for a test case by adding the timeout key to the test specification:

```yaml
timeout: 10 # seconds
```

Alternatively, a global default timeout can be set by providing an argument:

```bash
$ yastr --timeout 10
```

# Markers

Sometimes, only a subset of tests shall be run instead of executing all available ones. In pytest, this is usually done using markers applied to the test cases.

The same functionality is also available for yastr. It is even possible to reuse the same markers as for normal pytest test cases or even markers defined by plugins.

There are various ways how they are specified in the configuration file.

1. Just the name
    ```yaml
    markers:
        - skip  # Skip marker without any arguments
    ```
2. Name with positional arguments
    ```yaml
    markers:
        - [skip, [Skipped because of any reason]]
    ```
3. Name with keyword arguments
    ```yaml
    reason:
        - [skip, {reason: Skipped because of any reason}]
    ```

**Note that only markers on test case level are supported.**

Since yastr is based on pytest, tests with markers can be filtered by calling yastr with the same marker expression parameter (`-m`) as it exists for pytest:

```bash
yastr -m <MARKEXPR>
```

# Fixtures

For executing setup or teardown steps before or after each test case, so-called fixtures can be defined.

The handling is the same as for normal pytest fixtures where you create a function and decorate it with the pytest fixture decorator. This allows the use of already available fixtures as well as ones defined by other plugins.

A setup fixture could look like:

```python
from pytest import fixture


@fixture
def setup_test():
    ...
```

After defining it, it must be bound to the test case:

```yaml
fixtures:
    - setup_test
```

For teardown fixtures, the Python implementation could look like:

```python
from pytest import fixture


@fixture
def teardown_test():
    yield
    ...
```

**Note that `autouse` and fixtures on levels other than function level are currently not supported by yastr.**
