import subprocess
from os import chdir

from farmutils.helpers import run_host_cmd

def reset_repos(base_dir, repos, tag, default_tag=None, log_func=print):
    for repo in repos:
        log_func('Resetting repo [{}] to tag [{}]...'.format(repo, tag))
        chdir('{}/{}'.format(base_dir, repo))
        run_host_cmd("git fetch --all")
        try:
            run_host_cmd("git reset --hard {}".format(tag))
        except subprocess.CalledProcessError as e:
            if tag == default_tag or default_tag is None:
                log_func("Failed to reset repo [{}] to tag [{}]".format(
                    repo, tag))
                raise e
            else:
                log_func("Failed to reset repo [{}] to [{}] - so using default [{}]".format(
                    repo, tag, default_tag))
                run_host_cmd("git reset --hard {}".format(default_tag))


def get_latest_tag(srcdir, branch):
    chdir(srcdir)
    run_host_cmd("git fetch --all")
    tag, rc = run_host_cmd("git describe origin/{}".format(branch))
    return tag.rstrip()
