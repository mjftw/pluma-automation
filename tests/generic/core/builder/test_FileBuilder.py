import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from pluma.core.builder import CommandFileBuilder, TestsBuildError


def test_CommandFileBuilder_output_filepath_use_target_and_install_dir():
    output = 'myfile'
    install_dir = Path('mydir')
    builder = CommandFileBuilder(target_name=output, install_dir=install_dir,
                                 build_command='')
    assert builder.output_filepath.resolve() == install_dir.resolve() / output


def test_CommandFileBuilder_build_should_error_if_file_not_built():
    builder = CommandFileBuilder(target_name='any_name', build_command='')
    with pytest.raises(TestsBuildError):
        builder.build()


def test_CommandFileBuilder_build_should_return_path_to_file():
    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfilepath = Path(tmpfile.name)
        builder = CommandFileBuilder(install_dir=tmpfilepath.parent,
                                     target_name=tmpfilepath.name,
                                     build_command='')

        output_path = builder.build()
        assert output_path == str(builder.output_filepath)


def test_CommandFileBuilder_build_runs_build_command():
    build_cmd = 'some-build command'

    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfilepath = Path(tmpfile.name)
        builder = CommandFileBuilder(install_dir=tmpfilepath.parent,
                                     target_name=tmpfilepath.name,
                                     build_command=build_cmd)

        with patch('subprocess.check_output') as check_output:
            builder.build()

            check_output.assert_called_once()
            assert build_cmd in check_output.call_args[0]


def test_CommandFileBuilder_build_should_error_on_command_error():
    build_cmd = 'some-non-existant-build command'

    with tempfile.NamedTemporaryFile() as tmpfile:
        tmpfilepath = Path(tmpfile.name)
        builder = CommandFileBuilder(install_dir=tmpfilepath.parent,
                                     target_name=tmpfilepath.name,
                                     build_command=build_cmd)

        with pytest.raises(TestsBuildError):
            builder.build()


def test_CommandFileBuilder_install_folder_should_be_local():
    install = Path('mybuild')
    builder = CommandFileBuilder(target_name='abc', build_command='xyz',
                                 install_dir=install)
    assert str(builder.install_dir.resolve()).startswith(str(Path.cwd()))


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
