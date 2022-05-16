def test_str(pytester):
    pytester.makefile('.py', testfile='print("works!")')
    pytester.makefile('.yastr.json', config='{"executable": "python", "args": ["testfile.py"], "markers": ["skip"]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::config.yastr.json'


def test_args(pytester):
    pytester.makefile('.py', testfile='print("works!")')
    pytester.makefile('.yastr.json',
                      config='{"executable": "python", "args": ["testfile.py"], "markers": [["skip", ["foobar"]]]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::config.yastr.json'
    assert skipped[0].longrepr[2] == 'Skipped: foobar'


def test_kwargs(pytester):
    pytester.makefile('.py', testfile='print("works!")')
    pytester.makefile(
        '.yastr.json',
        config='{"executable": "python", "args": ["testfile.py"], "markers": [["skip", {"reason": "foobar"}]]}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not passed
    assert not failed
    assert skipped[0].nodeid == '.::config.yastr.json'
    assert skipped[0].longrepr[2] == 'Skipped: foobar'
