import shutil
import subprocess
import sys

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pluma.core.baseclasses import Logger

log = Logger()


class TestsBuildError(Exception):
    pass


class FileBuilder(ABC):
    '''Generic builder class to generate an output file from inputs.'''
    DEFAULT_BUILD_ROOT = Path.cwd()/'.pluma-build'

    def __init__(self, target_name: str, install_dir: str = None):
        self.target_name = target_name
        self.install_dir = Path(install_dir or FileBuilder.DEFAULT_BUILD_ROOT).resolve()

    @abstractmethod
    def build(self) -> str:
        '''Generate the output file, and return its path.'''

    @classmethod
    def clean(cls, force: bool = False):
        '''Clean build and output files.'''
        try:
            build_folder = cls.DEFAULT_BUILD_ROOT

            if not force:
                answer = input(
                    f'Do you confirm removing build folder "{build_folder}"? [yN]: ')
                if (answer != 'y'):
                    log.log('Aborting clean operation.')
                    return

            if build_folder == '' or build_folder == '/':
                raise TestsBuildError(
                    f'Refusing to clean build folder "{build_folder}"')

            shutil.rmtree(build_folder)
            log.log('Removed toolchain and test build folder')

        except Exception as e:
            raise TestsBuildError(
                f'Failed to clean build output: {e}')

    @property
    def output_filepath(self) -> Path:
        '''Return output file path'''
        return self.install_dir.joinpath(self.target_name)

    @staticmethod
    def create_directory(directory: Path):
        '''Create the directory or raise an error'''
        if not isinstance(directory, Path):
            raise ValueError('Expected a Path object')

        try:
            Path(directory).mkdir(exist_ok=True)
        except Exception as e:
            raise TestsBuildError(
                f'Failed to create build directory {directory}: {e}')


class CommandFileBuilder(FileBuilder):
    '''Generic builder class to generate an output file from inputs.'''

    def __init__(self, target_name: str, build_command: str, install_dir: str = None):
        super().__init__(target_name, install_dir)
        self.build_command = build_command

    def build(self) -> str:
        log.info(f'Build "{self.target_name}"...')
        FileBuilder.create_directory(self.install_dir)

        log.debug(f'Build command = {self.build_command}')

        try:
            out = subprocess.check_output(
                self.build_command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise TestsBuildError(
                f'Failed to build "{self.target_name}": {e.output.decode()}')

        log.debug(f'Build output = {out.decode()}')

        if not self.output_filepath.is_file():
            raise TestsBuildError(f'The build generated no output for target "{self.target_name}": '
                                  f'Expected file "{self.output_filepath}" does not exist.')

        return self.output_filepath


class YoctoCCrossCompiler(FileBuilder):
    '''Setup and cross-compile C tests with a Yocto SDK.

    Provide a set of methods to install a Yocto SDK, to find and
    source a Yocto SDK environment, and to cross compile a C
    application locally.
    '''
    DEFAULT_TOOLCHAIN_INSTALL_DIR = FileBuilder.DEFAULT_BUILD_ROOT/'yocto_toolchain'
    DEFAULT_EXEC_INSTALL_DIR = FileBuilder.DEFAULT_BUILD_ROOT/'yocto_c'

    def __init__(self, target_name: str, env_file: str, sources: List[str],
                 flags: List[str] = None, install_dir: str = None):
        super().__init__(target_name)
        self.env_file = env_file
        self.sources = sources
        self.flags = flags
        self.install_dir = install_dir

    def build(self) -> str:
        return YoctoCCrossCompiler.create_builder(target_name=self.target_name,
                                                  env_file=self.env_file,
                                                  sources=self.sources, flags=self.flags,
                                                  install_dir=self.install_dir).build()

    @staticmethod
    def install_yocto_sdk(yocto_sdk: str, install_dir: str = None) -> str:
        '''Install the Yocto SDK in a directory and return the directory used'''
        if not yocto_sdk or not isinstance(yocto_sdk, str):
            raise ValueError('Null Yocto SDK file path provided')

        yocto_sdk = Path(yocto_sdk).resolve()
        if not yocto_sdk.is_file():
            raise TestsBuildError(
                f'Failed to locate Yocto SDK "{yocto_sdk}" for C tests')

        if not install_dir:
            install_dir = YoctoCCrossCompiler.DEFAULT_TOOLCHAIN_INSTALL_DIR

        install_dir = Path(install_dir).resolve()
        YoctoCCrossCompiler.create_directory(install_dir)

        log.info('Installing Yocto SDK...')
        log.log([f'SDK: "{yocto_sdk}"',
                 'Destination: "{install_dir}"'])

        try:
            command = [yocto_sdk, '-y', '-d', install_dir]
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise TestsBuildError(
                f'Failed to install Yocto SDK: {e.output.decode()}')

        return install_dir

    @staticmethod
    def get_yocto_sdk_env_file(install_dir: str) -> str:
        '''Return the path to the Yocto SDK environment file in a folder or raise an error.'''
        env_file_pattern = 'environment-'
        for file in install_dir.iterdir():
            if str(file).startswith(env_file_pattern):
                return install_dir.pathjoin(file).resolve()

        raise TestsBuildError(
            f'No environment file ({env_file_pattern}) found in the toolchain '
            f'installation folder ({install_dir})')

    @classmethod
    def cross_compile(cls, target_name: str, env_file: str, sources: List[str],
                      flags: List[str] = None, install_dir: str = None) -> str:
        '''Cross-compile a C application with a Yocto SDK environment file and return its path'''
        return cls.create_builder(target_name=target_name, env_file=env_file,
                                  sources=sources, flags=flags,
                                  install_dir=install_dir).build()

    @staticmethod
    def create_builder(target_name: str, env_file: str, sources: List[str],
                       flags: List[str] = None, install_dir: str = None) -> FileBuilder:
        '''Return a builder to cross-compile a C application with a Yocto SDK'''
        if not target_name or not env_file or not sources:
            raise ValueError('Null target, environment or sources passed')

        if not install_dir:
            install_dir = YoctoCCrossCompiler.DEFAULT_EXEC_INSTALL_DIR

        if isinstance(sources, list):
            sources = ' '.join(sources)

        if not flags:
            flags = ''
        elif isinstance(flags, list):
            flags = ' '.join(flags)

        output_filepath = Path(install_dir).joinpath(target_name)
        command = f'. {env_file} && $CC {sources} {flags} -o {output_filepath}'
        return CommandFileBuilder(target_name=target_name, build_command=command,
                                  install_dir=install_dir)
