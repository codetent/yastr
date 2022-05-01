def test_executable(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat"}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'works!'
    assert passed[0].capstderr.strip() == ''


def test_args(pytester):
    pytester.makefile('.bat', testfile='@echo %1 %2')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "args": ["foo", "bar"]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'foo bar'
    assert passed[0].capstderr.strip() == ''


def test_env(pytester):
    pytester.makefile('.bat', testfile='@echo %FOO%')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "environment": {"FOO": "bar"}}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == ''


def test_skip(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
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
        '{"executable": "python", "args": ["-c", "import time; print(\\"foo\\", flush=True); time.sleep(100); print(\\"bar\\", flush=True);"], "timeout": 1}'
    )

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::config.yastr.json'
    assert failed[0].capstdout.strip() == 'foo'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext


def test_default_timeout(pytester):
    pytester.makefile(
        '.yastr.json',
        config=
        '{"executable": "python", "args": ["-c", "import time; print(\\"foo\\", flush=True); time.sleep(100); print(\\"bar\\", flush=True);"]}'
    )

    run = pytester.inline_run('--timeout=1', plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::config.yastr.json'
    assert failed[0].capstdout.strip() == 'foo'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext
