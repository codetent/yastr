def test_single_file(pytester):
    pytester.makefile('.bat', testfile='@echo works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.listoutcomes()[0][0]

    assert report.passed
    assert report.nodeid == '.::testfile.bat'
    assert report.capstdout.strip() == 'works!'
    assert report.capstderr.strip() == ''


def test_multiple_files(pytester):
    pytester.makefile('.bat', test_a='@echo a works!', test_b='@echo b works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])

    for name, report in zip(['a', 'b'], run.listoutcomes()[0]):
        assert report.passed
        assert report.nodeid == f'.::test_{name}.bat'
        assert report.capstdout.strip() == f'{name} works!'
        assert report.capstderr.strip() == ''


def test_subdir_files(pytester):
    moda_dir = pytester.mkdir('moda')
    (moda_dir / 'test.bat').write_text('@echo a works!')

    modb_dir = pytester.mkdir('modb')
    (modb_dir / 'test.bat').write_text('@echo b works!')

    run = pytester.inline_run(plugins=['yastr.plugin'])

    for name, report in zip(['a', 'b'], run.listoutcomes()[0]):
        assert report.passed
        assert report.nodeid == f'mod{name}::test.bat'
        assert report.capstdout.strip() == f'{name} works!'
        assert report.capstderr.strip() == ''
