import subprocess


def run_host_cmd(command, stdin=None, *args, **kwargs):
    ''' Wrapper for subprocess.Popen
    Runs the command @command in a subproccess
    returns a tuple of (<command output>, <returncode>)
    '''
    kwargs_final={
        'stdin': subprocess.PIPE,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT
    }

    if kwargs:
        kwargs_final.update(kwargs)

    child_proc = subprocess.Popen(
        command.split(), *args, **kwargs_final)
    return (child_proc.communicate(
        input=None if not stdin else bytes(stdin, 'utf-8')
    )[0].decode('utf-8'), child_proc.returncode)