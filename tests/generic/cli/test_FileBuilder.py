import time
import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from pluma.cli import CommandFileBuilder, TestsBuildError


def test_CommandFileBuilder_output_filepath_use_target_and_install_dir():
    output = 'myfile'
    install_dir = 'mydir'
    builder = CommandFileBuilder(target_name=output, install_dir=install_dir, build_command='')
    assert builder.output_filepath == Path(install_dir).resolve() / output


def test_CommandFileBuilder_build_should_error_if_file_not_built():
    builder = CommandFileBuilder(target_name='any_name', build_command='')
    with pytest.raises(TestsBuildError):
        builder.build()


def test_CommandFileBuilder_build_should_return_path_to_file():
    builder = CommandFileBuilder(target_name='any_name', build_command='')

    # Create output file to ignore build error
    with open(builder.output_filepath, 'w') as output_file:
        output_path = builder.build()
        assert output_path == builder.output_filepath
        os.remove(output_file.name)


def test_CommandFileBuilder_build_runs_build_command():
    output = 'myfile'
    build_cmd = 'some-build command'
    builder = CommandFileBuilder(target_name=output, build_command=build_cmd)

    with open(builder.output_filepath, 'w') as output_file:
        with patch('subprocess.check_output') as check_output:
            builder.build()

            check_output.assert_called_once()
            assert build_cmd in check_output.call_args[0]

        os.remove(output_file.name)


def test_CommandFileBuilder_build_should_error_on_command_error():
    output = 'myfile'
    build_cmd = 'some-non-existant-build command'
    builder = CommandFileBuilder(target_name=output, build_command=build_cmd)

    with open(builder.output_filepath, 'w') as output_file:
        with pytest.raises(TestsBuildError):
            builder.build()

        os.remove(output_file.name)


def test_CommandFileBuilder_install_folder_should_be_local():
    install = 'mybuild'
    builder = CommandFileBuilder(target_name='abc', build_command='xyz', install_dir=install)
    assert str(builder.install_dir).startswith(str(Path.cwd()))


def test_CommandFileBuilder_install_folder_should_defaults_to_local_build_folder():
    builder = CommandFileBuilder(target_name='abc', build_command='xyz')
    assert builder.output_filepath != Path.cwd()
    assert str(builder.output_filepath).startswith(str(Path.cwd()))


def test_CommandFileBuilder_clean_should_remove_build_folder():
    builder = CommandFileBuilder(target_name='myfile', build_command='')
    builder.install_dir.mkdir(exist_ok=True)
    assert builder.install_dir.is_dir()

    builder.clean(force=True)

    assert not builder.install_dir.is_dir()
