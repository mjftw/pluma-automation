import tempfile
import pytest
from pathlib import Path

from pluma.core.builder import FileBuilder, TestsBuildError, YoctoCBuilder


def test_YoctoCBuilder_get_yocto_sdk_env_file_error_if_no_env_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir).joinpath('somefile').touch()

        with pytest.raises(TestsBuildError):
            YoctoCBuilder.get_yocto_sdk_env_file(install_dir=Path(tmpdir))


def test_YoctoCBuilder_get_yocto_sdk_env_file_finds_env_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir).joinpath('environment-toolchainname')
        env_file.touch()
        env_returned = YoctoCBuilder.get_yocto_sdk_env_file(
            install_dir=Path(tmpdir))

        assert env_file == env_returned


def test_YoctoCBuilder_create_builder_should_error_on_missing_sources():
    target = 'abc'
    env_file = 'environment-something'
    sources = []
    flags = ['-d', '-a']

    with pytest.raises(ValueError):
        YoctoCBuilder.create_builder(target_name=target, env_file=Path(env_file),
                                     flags=flags, sources=sources)


def test_YoctoCBuilder_create_builder_should_error_on_missing_env_file():
    target = 'abc'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']

    with pytest.raises(ValueError):
        YoctoCBuilder.create_builder(target_name=target,
                                     flags=flags, sources=sources)


def test_YoctoCBuilder_create_builder_should_return_builder():
    target = 'abc'
    env_file = 'environment-something'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']

    builder = YoctoCBuilder.create_builder(target_name=target, env_file=Path(env_file),
                                           flags=flags, sources=sources)
    assert isinstance(builder, FileBuilder)


def test_YoctoCBuilder_create_builder_should_generate_correct_build_command():
    target = 'abc'
    env_file = 'environment-something'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']
    src_string = ' '.join(sources)
    flags_string = ' '.join(flags)

    builder = YoctoCBuilder.create_builder(target_name=target, env_file=Path(env_file),
                                           flags=flags, sources=sources)

    target_fullpath = builder.install_dir/target
    expected_cmd = f'. {env_file} && $CC {src_string} {flags_string} -o {target_fullpath}'
    assert builder.build_command == expected_cmd
