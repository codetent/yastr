# Quickstart

## Install yastr

There are multiple ways for installing yastr. In this quickstart guide we directly install the Python package:

```bash
$ pip install yapf
```

## Create first test

Before creating the test case, you first need the test executable that should be called. For demonstration purposes, we
are calling python with some arguments.

Each test case is specified using a file ending with `.yastr.json` or `.yastr.yaml`. This specification lists all
information required for the test case:

```yaml
executable: python
args: [-c, "import os; print(os.environ['VAR']")]
environment:
    VAR: foobar
```

This configuration defines that python shall be called with an inline script which prints out the `VAR` environment variable. The value of it is set below to `foobar`.

## Running first test

After creating the configuration file, the test can be run by simply calling in the directory where you placed it:

```bash
$ yastr
```


## Advanced

### Skipping

For development reasons, single test cases can be skipped by setting the `skip` option:

```yaml
skip: True
```

### Timeout

Sometimes, test executables can be stuck or just last very long. In this case it could make sense to set a timeout after which the test should be aborted. After exceeding it, the current executable will be killed and the test runner will proceeed.

It can be enabled by adding the timeout key to the test specification:

```yaml
timeout: 10 # seconds
```

Alternatively, a global default timeout can be set by providing an argument:

```bash
$ yastr --timeout 10
```
