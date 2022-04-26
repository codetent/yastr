def test_str(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat", "markers": ["skip"]}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::testfile.bat'


def test_args(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.json', **{'test-config': '{"executable": "testfile.bat", "markers": [["skip", ["foobar"]]]}'})

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::testfile.bat'
    assert skipped[0].longrepr[2] == 'Skipped: foobar'


def test_kwargs(pytester):
    pytester.makefile('.bat', testfile='@echo works!')
    pytester.makefile('.json', **{
        'test-config': '{"executable": "testfile.bat", "markers": [["skip", {"reason": "foobar"}]]}',
    })

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::testfile.bat'
    assert skipped[0].longrepr[2] == 'Skipped: foobar'
