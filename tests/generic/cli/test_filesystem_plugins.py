import os
import stat
import re
from pathlib import Path
import pytest

from pluma.plugins.testsuite import filesystem


def check_capsys_for_test_fail(test_cls, capsys):
    stdout = capsys.readouterr().out
    testname = test_cls.__name__

    return bool(re.search(rf'{testname}.+FAIL', stdout))


def test_filesystem_FileExists_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileExists, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileExists_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    test_config = pluma_config_file([
        (filesystem.FileExists, {
            'path': '/theres/no/way/this/file/actually/exists!',
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileExists, capsys)


def test_filesystem_FileIsRegular_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsRegular, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsRegular_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    test_config = pluma_config_file([
        (filesystem.FileIsRegular, {
            'path': Path(__file__).parent,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsRegular, capsys)


def test_filesystem_FileIsDir_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsDir, {
            'path': Path(__file__).parent,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsDir_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    test_config = pluma_config_file([
        (filesystem.FileIsDir, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsDir, capsys)


def test_filesystem_FileIsNotEmpty_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsNotEmpty, {
            'path': temp_file('Foobar'),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsNotEmpty_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    test_config = pluma_config_file([
        (filesystem.FileIsNotEmpty, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsNotEmpty, capsys)


def test_filesystem_FileIsEmpty_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsEmpty, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsEmpty_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    test_config = pluma_config_file([
        (filesystem.FileIsEmpty, {
            'path': temp_file('Foobar'),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsEmpty, capsys)


def test_filesystem_FileIsReadable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsReadable, {
            'path': __file__,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsReadable_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    filename = temp_file()
    perms = os.stat(filename)
    os.chmod(filename, perms.st_mode & ~stat.S_IREAD)

    test_config = pluma_config_file([
        (filesystem.FileIsReadable, {
            'path': filename,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsReadable, capsys)

def test_filesystem_FileIsWritable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    test_config = pluma_config_file([
        (filesystem.FileIsWritable, {
            'path': temp_file(),
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsWritable_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    filename = temp_file()
    perms = os.stat(filename)
    os.chmod(filename, perms.st_mode & ~stat.S_IWRITE)

    test_config = pluma_config_file([
        (filesystem.FileIsWritable, {
            'path': filename,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsWritable, capsys)

def test_filesystem_FileIsExecutable_should_pass_when_true(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file()
    perms = os.stat(filename)
    os.chmod(filename, perms.st_mode | stat.S_IEXEC)

    test_config = pluma_config_file([
        (filesystem.FileIsExecutable, {
            'path': filename,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_FileIsExecutable_should_fail_when_false(pluma_cli, temp_file, pluma_config_file, capsys):
    filename = temp_file()

    test_config = pluma_config_file([
        (filesystem.FileIsExecutable, {
            'path': filename,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.FileIsExecutable, capsys)


def test_filesystem_CheckFileSize_should_pass_when_file_over_min(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file('The quick brown fox jumped over the lazy dog')

    test_config = pluma_config_file([
        (filesystem.CheckFileSize, {
            'path': filename,
            'min': 10,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_CheckFileSize_should_fail_when_file_under_min(pluma_cli, temp_file, pluma_config_file, capsys):
    filename = temp_file('The quick brown fox jumped over the lazy dog')

    test_config = pluma_config_file([
        (filesystem.CheckFileSize, {
            'path': filename,
            'min': 1000,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.CheckFileSize, capsys)


def test_filesystem_CheckFileSize_should_pass_when_file_under_max(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file('The quick brown fox jumped over the lazy dog')

    test_config = pluma_config_file([
        (filesystem.CheckFileSize, {
            'path': filename,
            'max': 1000,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])


def test_filesystem_CheckFileSize_should_fail_when_file_over_max(pluma_cli, temp_file, pluma_config_file, capsys):
    filename = temp_file('The quick brown fox jumped over the lazy dog')

    test_config = pluma_config_file([
        (filesystem.CheckFileSize, {
            'path': filename,
            'max': 10,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
    assert check_capsys_for_test_fail(filesystem.CheckFileSize, capsys)


def test_filesystem_CheckFileSize_should_pass_when_file_in_range(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file('The quick brown fox jumped over the lazy dog')

    test_config = pluma_config_file([
        (filesystem.CheckFileSize, {
            'path': filename,
            'min': 10,
            'max': 1000,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
