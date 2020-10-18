import tempfile
import pytest
from pathlib import Path

from pluma.core.builder import FileBuilder, TestsBuildError, YoctoCCrossCompiler


def test_YoctoCBuilder_get_yocto_sdk_env_file_error_if_no_env_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir).joinpath('somefile').touch()

        with pytest.raises(TestsBuildError):
            YoctoCCrossCompiler.get_yocto_sdk_env_file(install_dir=tmpdir)


def test_YoctoCBuilder_get_yocto_sdk_env_file_finds_env_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir).joinpath('environment-toolchainname')
        env_file.touch()
        env_returned = YoctoCCrossCompiler.get_yocto_sdk_env_file(
            install_dir=tmpdir)

        assert env_file == env_returned


def test_YoctoCBuilder_create_builder_should_error_on_missing_sources():
    target = 'abc'
    env_file = 'environment-something'
    sources = []
    flags = ['-d', '-a']

    with pytest.raises(ValueError):
        YoctoCCrossCompiler.create_builder(target_name=target, env_file=env_file,
                                           flags=flags, sources=sources)


def test_YoctoCBuilder_create_builder_should_error_on_missing_env_file():
    target = 'abc'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']

    with pytest.raises(TypeError):
        YoctoCCrossCompiler.create_builder(target_name=target,
                                           flags=flags, sources=sources)


def test_YoctoCBuilder_create_builder_should_return_builder():
    target = 'abc'
    env_file = 'environment-something'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']

    builder = YoctoCCrossCompiler.create_builder(target_name=target, env_file=env_file,
                                                 flags=flags, sources=sources)
    assert isinstance(builder, FileBuilder)


def test_YoctoCBuilder_create_builder_should_generate_correct_build_command():
    target = 'abc'
    env_file = 'environment-something'
    sources = ['main.c', 'other.c']
    flags = ['-d', '-a']
    src_string = ' '.join(sources)
    flags_string = ' '.join(flags)

    builder = YoctoCCrossCompiler.create_builder(target_name=target, env_file=env_file,
                                                 flags=flags, sources=sources)

    target_fullpath = Path(builder.install_dir)/target
    expected_cmd = f'. {env_file} && $CC {src_string} {flags_string} -o {target_fullpath}'
    assert builder.build_command == expected_cmd
