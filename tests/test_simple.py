def test_single_file(pytester):
    pytester.makefile('.bat', testfile='@echo works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::testfile.bat'
    assert passed[0].capstdout.strip() == 'works!'
    assert passed[0].capstderr.strip() == ''


def test_multiple_files(pytester):
    pytester.makefile('.bat', test_a='@echo a works!', test_b='@echo b works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed

    for name, report in zip(['a', 'b'], passed):
        assert report.nodeid == f'.::test_{name}.bat'
        assert report.capstdout.strip() == f'{name} works!'
        assert report.capstderr.strip() == ''


def test_subdir_files(pytester):
    moda_dir = pytester.mkdir('moda')
    (moda_dir / 'test.bat').write_text('@echo a works!')

    modb_dir = pytester.mkdir('modb')
    (modb_dir / 'test.bat').write_text('@echo b works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed

    for name, report in zip(['a', 'b'], passed):
        assert report.nodeid == f'mod{name}::test.bat'
        assert report.capstdout.strip() == f'{name} works!'
        assert report.capstderr.strip() == ''


def test_executable(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat"}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::testfile.bat'
    assert passed[0].capstdout.strip() == 'works!'
    assert passed[0].capstderr.strip() == ''


def test_args(pytester):
    pytester.makefile('.bat', testfile='@echo %1 %2')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat", "args": ["foo", "bar"]}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::testfile.bat'
    assert passed[0].capstdout.strip() == 'foo bar'
    assert passed[0].capstderr.strip() == ''


def test_env(pytester):
    pytester.makefile('.bat', testfile='@echo %FOO%')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat", "environment": {"FOO": "bar"}}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::testfile.bat'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == ''


def test_skip(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat", "skip": "true"}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::testfile.bat'


def test_timeout(pytester):
    pytester.makefile(
        '.json', **{
            'test-config':
            '{"executable": "python", "args": ["-c", "import time; print(\\"foo\\", flush=True); time.sleep(100); print(\\"bar\\", flush=True);"], "timeout": 1}'
        })

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::python'
    assert failed[0].capstdout.strip() == 'foo'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext


def test_default_timeout(pytester):
    pytester.makefile(
        '.json', **{
            'test-config':
            '{"executable": "python", "args": ["-c", "import time; print(\\"foo\\", flush=True); time.sleep(100); print(\\"bar\\", flush=True);"]}'
        })

    run = pytester.inline_run('--timeout=1', plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not skipped
    assert failed[0].nodeid == '.::python'
    assert failed[0].capstdout.strip() == 'foo'
    assert failed[0].capstderr.strip() == ''
    assert 'Executable timed out after 1.0 second(s)' in failed[0].longreprtext
