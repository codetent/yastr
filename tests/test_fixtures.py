def test_setup(pytester):
    pytester.makefile('.bat', testfile='@echo bar')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "fixtures": ["foo"]}')
    pytester.makeconftest('''
        import pytest
        import sys

        @pytest.fixture
        def foo():
            print('foo', flush=True, file=sys.stderr)
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == 'foo'


def test_yield(pytester):
    pytester.makefile('.bat', testfile='@echo bar')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "fixtures": ["foo"]}')
    pytester.makeconftest('''
        import pytest
        import sys

        @pytest.fixture
        def foo():
            print('foo', flush=True, file=sys.stderr)
            yield
            print('end', flush=True, file=sys.stderr)
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == 'foo\nend'


def test_dependency_single(pytester):
    pytester.makefile('.bat', testfile='@echo bar')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "fixtures": ["foo"]}')
    pytester.makeconftest('''
        import pytest
        import sys

        @pytest.fixture
        def bar():
            print('bar', flush=True, file=sys.stderr)

        @pytest.fixture
        def foo(bar):
            print('foo', flush=True, file=sys.stderr)
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == 'bar\nfoo'


def test_dependency_multiple(pytester):
    pytester.makefile('.bat', testfile='@echo bar')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "fixtures": ["c"]}')
    pytester.makeconftest('''
        import pytest
        import sys

        @pytest.fixture
        def a():
            print('a', flush=True, file=sys.stderr)

        @pytest.fixture
        def b():
            print('b', flush=True, file=sys.stderr)

        @pytest.fixture
        def c(a, b):
            print('c', flush=True, file=sys.stderr)
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == 'a\nb\nc'


def test_dependency_diamond(pytester):
    pytester.makefile('.bat', testfile='@echo bar')
    pytester.makefile('.yastr.json', config='{"executable": "testfile.bat", "fixtures": ["d"]}')
    pytester.makeconftest('''
        import pytest
        import sys

        @pytest.fixture
        def a():
            print('a', flush=True, file=sys.stderr)

        @pytest.fixture
        def b(a):
            print('b', flush=True, file=sys.stderr)

        @pytest.fixture
        def c(a):
            print('c', flush=True, file=sys.stderr)

        @pytest.fixture
        def d(b, c):
            print('d', flush=True, file=sys.stderr)
    ''')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    passed, skipped, failed = run.listoutcomes()

    assert not skipped
    assert not failed
    assert passed[0].nodeid == '.::config.yastr.json'
    assert passed[0].capstdout.strip() == 'bar'
    assert passed[0].capstderr.strip() == 'a\nb\nc\nd'
