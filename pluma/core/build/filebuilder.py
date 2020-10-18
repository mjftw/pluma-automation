import shutil
import subprocess

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
