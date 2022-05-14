def test_setting(pytester):
    pytester.makefile('.py',
                      driver='import sys; from subprocess import run; print("foo", flush=True); run(sys.argv[1:])')
    pytester.makefile('.yastr.json', config='{"executable": "python", "args": ["-c", "print(\'bar\')"]}')
    pytester.makefile('.ini', pytest="[pytest]\ntest_driver=python driver.py")

    run = pytester.inline_run(
        '--ignore=pytest.ini',
        '--ignore=redirect.bat',
        plugins=['yastr.plugin'],
    )
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'foo\nbar'
    assert passed[0].capstderr.strip() == ''
