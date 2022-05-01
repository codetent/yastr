def test_file_empty_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.json', config='')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: Invalid configuration values' in report.longreprtext


def test_file_missing_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.json', config='{"skip": true}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: Invalid configuration values' in report.longreprtext
    assert '\'executable\': [\'Missing data for required field\']'


def test_file_wrong_config(pytester):
    pytester.makefile('.txt', testfile='')
    pytester.makefile('.yastr.json', config='{"executable": 1, "new": "false"}')

    run = pytester.inline_run(plugins=['yastr.plugin'])
    report = run.getfailures()[0]

    assert report.failed
    assert 'ConfigError: Invalid configuration values' in report.longreprtext
    assert '\'executable\': [\'Not a valid string.\']'
    assert '\'new\': [\'Unknown field.\']'
