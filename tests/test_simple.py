def test_executable(pytester):
    pytester.makefile('.py', testfile='print("works!")')
    pytester.makefile('.yastr.json', config='{"executable": "python", "args": ["testfile.py"]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'works!'
    assert passed[0].capstderr.strip() == ''


def test_args(pytester):
    pytester.makefile('.py', testfile='import sys; print(sys.argv[1], sys.argv[2])')
    pytester.makefile('.yastr.json', config='{"executable": "python", "args": ["testfile.py", "foo", "bar"]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'foo bar'
    assert passed[0].capstderr.strip() == ''


def test_env(pytester):
    pytester.makefile('.py', testfile='import os; print(os.environ["FOO"])')
    pytester.makefile('.yastr.json',
                      config='{"executable": "python", "args": ["testfile.py"], "environment": {"FOO": "bar"}}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == ''


def test_skip(pytester):
    pytester.makefile('.py', testfile='print("works!")')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "skip": "true"}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::config.yastr.json'


def test_timeout(pytester):
    pytester.makefile(
        '.yastr.json',
        config=
        '{"executable": "python", "args": ["-c", "import time; print(1, flush=True); time.sleep(100); print(2, flush=True);"], "timeout": 1}'
    )

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::config.yastr.json'
    assert failed[0].capstdout.strip() == '1'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext


def test_default_timeout(pytester):
    pytester.makefile(
        '.yastr.json',
        config=
        '{"executable": "python", "args": ["-c", "import time; print(1, flush=True); time.sleep(100); print(2, flush=True);"]}'
    )

    run = pytester.inline_run('--timeout=1', plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::config.yastr.json'
    assert failed[0].capstdout.strip() == '1'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext
