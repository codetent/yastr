def test_setting(pytester):
    pytester.makefile('.bat', testfile='@echo bar', redirect='@echo foo&& %*')
    pytester.makefile('.ini', pytest="[pytest]\ntest_driver=redirect.bat")

    run = pytester.inline_run(
        '--ignore=pytest.ini',
        '--ignore=redirect.bat',
        plugins=['yastr.plugin'],
    )
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::testfile.bat'
    assert passed[0].capstdout.strip() == 'foo\nbar'
    assert passed[0].capstderr.strip() == ''
