import subprocess


def run_host_cmd(command, *args, **kwargs):
    ''' Wrapper for subprocess.Popen
    Runs the command @command in a subproccess
    returns a tuple of (<command output>, <returncode>)
    '''
    kwargs_final={'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE}
    if kwargs:
        kwargs_final.update(kwargs)

    child_proc = subprocess.Popen(
        command.split(), *args, **kwargs_final)
    return (child_proc.communicate()[0].decode('utf-8'), child_proc.returncode)