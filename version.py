import subprocess


def git_is_installed():
    try:
        subprocess.check_call(['which', 'git'], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

def get_farmcore_version():
    ''' Find the current farm-core version from git tags using git-describe '''
    if not git_is_installed():
        raise EnvironmentError(
            '\n\nThe tool "git" must be installed on the system to install '
            'this package.\n'
            'See: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git\n'
        )

    version = subprocess.check_output(
        ['git', 'describe', '--tags', '--always', '--match', 'v*.*.*'])
    return version.decode('utf-8').strip()