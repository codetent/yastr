def test_file_empty_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.yaml', config='')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: Invalid configuration values' in report.longreprtext


def test_file_missing_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.yaml', config='skip: true')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: could not determine a constructor for the tag None' in report.longreprtext


def test_file_wrong_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.yaml', config='executable: 1\nnew: "false"}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: while parsing a block mapping' in report.longreprtext
