import subprocess
import json


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


def format_json_for_vc(db_file, db_output_file):
    '''
    Formats a packed json file with line separators and key ordering
    so that it can be committed to version control.
    '''
    with open(db_file) as f:
        db_str = f.read()

    db_dict = json.loads(db_str)
    db_json = json.dumps(db_dict,
        sort_keys=True, indent=4, separators=(',', ': '))

    with open(db_output_file, 'w') as f:
        f.writelines(db_json)