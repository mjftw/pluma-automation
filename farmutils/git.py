import subprocess
from os import chdir


def reset_repos(base_dir, repos, tag, default_tag=None):
    for repo in repos:
        print("Changing to {}/{}....".format(base_dir, repo))
        chdir('{}/{}'.format(base_dir, repo))
        _run("git fetch --all")
        try:
            _run("git reset --hard {}".format(tag))
        except subprocess.CalledProcessError as e:
            if tag == default_tag:
                print("Failed to reset repo [{}] to tag [{}]".format(
                    repo, tag))
                raise e
            else:
                print("Failed to reset repo [{}] to [{}] - so using default [{}]".format(
                    repo, tag, default_tag))
                _run("git reset --hard {}".format(default_tag))


def get_latest_tag(srcdir, branch):
    chdir(srcdir)
    _run("git fetch --all")
    tag = _run("git describe origin/{}".format(branch), stdout=subprocess.PIPE)
    tag = tag.stdout.decode('ascii').strip()
    return tag


def _run(cmd, *args, **kwargs):
    kwargs['check'] = True
    return subprocess.run(cmd.split(), *args, **kwargs)
