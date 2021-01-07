import subprocess
import json
import re
import inspect
from pathlib import PurePath
from datetime import datetime
from typing import Tuple, Optional, Type, Any

ROOT_PROJECT_DIRECTORY = PurePath(__file__).parents[2]

def run_host_cmd(command, stdin=None, *args, **kwargs):
    ''' Wrapper for subprocess.Popen
    Runs the command @command in a subproccess
    returns a tuple of (<command output>, <returncode>)
    '''
    kwargs_final = {
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
        db_dict[t] = {int(x): db_dict[t][x] for x in db_dict[t].keys()}

    db_json = json.dumps(db_dict,
                         sort_keys=True, indent=4, separators=(',', ': '))

    with open(db_output_file, 'w') as f:
        f.writelines(db_json)


def timestamp_to_datetime(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%d-%H-%M-%S')


def datetime_to_timestamp(dt):
    return dt.strftime('%Y-%m-%d-%H-%M-%S')


def regex_filter_list(patterns, items, unique=None):
    '''
    Get a list of items from @items that match any of the regular
    expressions @patterns.
    Returned list is alphanumerically sorted.
    If @unique, duplicates are removed.
    '''
    gen = (i for p, i in filter(lambda pi: re.match(*pi),
                                (((p, i) for i in items for p in patterns))))
    if unique:
        gen = set(gen)
    return sorted(gen)

def get_file_and_line(obj: Type[Any], relative_to: PurePath = ROOT_PROJECT_DIRECTORY) -> Tuple[Optional[PurePath], Optional[int]]:
    '''
    Get the filename and line number of a given
    python object type (@obj). Useful for creating a stack trace.
    The filename will be relative to @relative_to for easy printing.
    The default value of @relative_to is the project root of this library.
    '''
    src_file = inspect.getsourcefile(obj)
    if src_file is None:
        return (None, None)
    src_path = PurePath(src_file)
    src_line = inspect.getsourcelines(obj)[1]
    try:
        rel_path = src_path.relative_to(relative_to)
    except:
        return (src_path, src_line)
    else:
        return (rel_path, src_line)
