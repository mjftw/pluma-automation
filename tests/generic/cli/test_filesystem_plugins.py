import os
import stat
from pluma.plugins.testsuite import filesystem


def test_filesystem_FileExists_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileExists, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsRegular_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsRegular, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsNotEmpty_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsRegular, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsEmpty_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsRegular, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsReadable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsReadable, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsWritable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsWritable, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsExecutable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file()
    perms = os.stat(filename)
    os.chmod(filename, perms.st_mode | stat.S_IEXEC)

    test_config = pluma_config_file([
        (filesystem.FileIsExecutable, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
