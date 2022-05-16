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
