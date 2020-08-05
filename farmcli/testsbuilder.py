import subprocess
import os.path
import sys
import shutil
from farmcore.baseclasses import Logger, LogLevel

log = Logger()


class TestsBuildError(Exception):
    pass


class TestsBuilder:
    '''Setup and cross-compile C tests with a Yocto SDK.

    Provide a set of methods to install a Yocto SDK, to find and
    source a Yocto SDK environment, and to cross compile a C
    application locally.
    '''
    DEFAULT_BUILD_ROOT = os.path.join(os.path.dirname(
        os.path.abspath(sys.modules['__main__'].__file__)), 'build')
    DEFAULT_TOOLCHAIN_INSTALL_DIR = os.path.join(
        DEFAULT_BUILD_ROOT, 'toolchain')
    DEFAULT_EXEC_INSTALL_DIR = os.path.join(DEFAULT_BUILD_ROOT, 'ctests')

    @staticmethod
    def create_directory(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise ValueError(
                f'Failed to create build directory {directory}: {e}')

    @staticmethod
    def install_yocto_sdk(yocto_sdk, install_dir=None):
        if not yocto_sdk or not isinstance(yocto_sdk, str):
            raise ValueError('Null Yocto SDK file path provided')

        yocto_sdk = os.path.abspath(yocto_sdk)
        if not os.path.isfile(yocto_sdk):
            raise TestsBuildError(
                f'Failed to locate Yocto SDK "{yocto_sdk}" for C tests')

        if not install_dir:
            install_dir = TestsBuilder.DEFAULT_TOOLCHAIN_INSTALL_DIR

        install_dir = os.path.abspath(install_dir)
        TestsBuilder.create_directory(install_dir)

        log.log(
            f'Installing Yocto SDK...', level=LogLevel.INFO)
        log.log(
            f'  SDK: "{yocto_sdk}"\n  Destination: "{install_dir}"')

        try:
            command = [yocto_sdk, '-y', '-d', install_dir]
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise TestsBuildError(
                f'Failed to install Yocto SDK: {e.output.decode()}')

        return install_dir

    @staticmethod
    def find_yocto_sdk_env_file(install_dir):
        '''Search for a Yocto SDK environment file in a folder.'''
        env_file_pattern = 'environment-'
        for file in os.listdir(install_dir):
            if file.startswith(env_file_pattern):
                return os.path.abspath(f'{install_dir}/{file}')

        raise TestsBuildError(
            f'No environment file ({env_file_pattern}) found in the toolchain installation folder ({install_dir})')

    @staticmethod
    def build_c_test(target_name, env_file, sources, flags=None, install_dir=None):
        '''Cross-compile a C application with a Yocto SDK environment file.'''
        if not target_name or not env_file or not sources:
            raise ValueError('Null target, environment or sources passed')

        if not install_dir:
            install_dir = TestsBuilder.DEFAULT_EXEC_INSTALL_DIR

        if isinstance(sources, list):
            sources = ' '.join(sources)

        if not flags:
            flags = ''
        elif isinstance(flags, list):
            flags = ' '.join(flags)

        install_dir = os.path.abspath(install_dir)
        TestsBuilder.create_directory(install_dir)
        target_filepath = os.path.join(install_dir, target_name)

        log.log(f'Cross compiling "{target_name}"...', level=LogLevel.INFO)
        command = f'. {env_file} && $CC {sources} {flags} -o {target_filepath}'
        log.debug(f'Build command = {command}')

        try:
            out = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise TestsBuildError(
                f'Failed to build "{target_name}": {e.output.decode()}')

        log.debug(f'Build output = {out.decode()}')

        return target_filepath

    @staticmethod
    def clean(force=False):
        '''Clean build files.'''
        try:
            # TODO: Would need to use actual build folder and list of built/installed
            # files
            build_folder = TestsBuilder.DEFAULT_BUILD_ROOT

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
