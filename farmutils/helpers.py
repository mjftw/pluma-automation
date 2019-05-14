import subprocess
import json
from datetime import datetime as dt

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


def format_json_tinydb(db_file, db_output_file):
    '''
    Formats a TinyDB json database with line separators and key ordering
    so that it can be committed to version control.
    '''
    with open(db_file) as f:
        db_str = f.read()

    db_dict = json.loads(db_str)

    # Convert ids from str to int so that they order properly
    for t in db_dict:
        db_dict[t] = {int(x):db_dict[t][x] for x in db_dict[t].keys()}

    db_json = json.dumps(db_dict,
        sort_keys=True, indent=4, separators=(',', ': '))

    with open(db_output_file, 'w') as f:
        f.writelines(db_json)


def timestamp_to_datetime(timestamp):
    return dt.strptime(timestamp,'%Y-%m-%d-%H-%M-%S')


def datetime_to_timestamp(datetime):
    return datetime.strftime('%Y-%m-%d-%H-%M-%S')