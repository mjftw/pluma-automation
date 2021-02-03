import subprocess
import re
import inspect
from pathlib import PurePath
from datetime import datetime
from typing import Tuple, Optional, Type, Any

ROOT_PROJECT_DIRECTORY = PurePath(__file__).parents[2]


def run_host_cmd(command: str, stdin: Optional[str] = None, *args,
                 **kwargs) -> Tuple[str, int]:
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

    child_proc = subprocess.Popen(command.split(), *args, **kwargs_final)
    output, _ = child_proc.communicate(input=None if not stdin else stdin)

    return output, child_proc.returncode


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


FileAndLine = Tuple[Optional[PurePath], Optional[int]]


def get_file_and_line(obj: Type[Any],
                      relative_to: PurePath = ROOT_PROJECT_DIRECTORY) -> FileAndLine:
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
    except ValueError:
        return (src_path, src_line)
    else:
        return (rel_path, src_line)


def resize_string(text: str, length: int) -> str:
    '''Pad or elide a string to be exactly "length" long'''
    if length < 4:
        raise ValueError('Length must be 4 or more, to fit the elide characters')

    if len(text) > length:
        return f'{text[:length-3]}...'
    else:
        return text.ljust(length)
