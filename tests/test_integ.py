def test_python(pytester):
    pytester.makefile('.yastr.json', config='{"executable": "python", "args": ["-c", "print(\'bar\')"]}')
    pytester.makepyfile(test_dummy='''
        def test_foo():
            print('foo')
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert len(passed) == 2

    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == ''

    assert passed[1].nodeid == 'test_dummy.py::test_foo'
    assert passed[1].capstdout.strip() == 'foo'
    assert passed[1].capstderr.strip() == ''
