import subprocess


def run_host_cmd(command):
    ''' Wrapper for subprocess.Popen
    Runs the command @command in a subproccess
    returns a tuple of (<command output>, <returncode>)
    '''
    child_proc = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (child_proc.communicate()[0].decode('utf-8'), child_proc.returncode)