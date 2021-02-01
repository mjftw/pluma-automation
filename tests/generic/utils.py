import os
from select import select
from multiprocessing.pool import ThreadPool
from typing import Dict, Any, List, Union


def fd_has_data(fd, timeout=0):
    readable_fd_list, __, __ = select([fd], [], [], timeout)
    return fd in readable_fd_list


class OsFile:
    def __init__(self, fd, encoding=None):
        self.fd = fd
        self.encoding = encoding

    def read(self, n=None, timeout=None):
        if timeout is not None and not fd_has_data(self.fd, timeout):
            raw = b''
        else:
            raw = os.read(self.fd, n or 10000)

        if self.encoding:
            msg = raw.decode(self.encoding)
        else:
            msg = raw

        return msg

    def write(self, msg):
        if self.encoding:
            msg = msg.encode(self.encoding)

        return os.write(self.fd, msg)


def nonblocking(f, *args, **kwargs):
    ''' Run function f without blocking, returning an async_result handle

    Caller must call get() on the returned object to get the function return
    value. E.g.
    async_result = nonblocking(myFunction, 1, 2, 3, a='foo', b='bar')
    ...
    # Do other things
    ...
    myFunction_return_value = async_result.get()
    '''
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(f, args=args, kwds=kwargs)
    return async_result


class PlumaOutputMatcher:
    '''
    Match a Pluma output object with an expected output, ignoring any
    extra information that may be appended to the name of the test in the output.

    For example, we might have an expected output that looks something like this:
    {
        "myplugin.thing": { ... }
    }
    But the actual output might look like, where the number 10 will change across
    test runs:
    {
        "myplugin.thing#10": { ... }
    }
    To account for this variance, this function checks the top level names seperate
    from the top level values, and uses a "expected is in actual" approach to names
    instead of perfect equality.

    You can use this assertion like so:
    assert PlumaOutputMatcher(['myplugin.thing', 'myplugin.thing2'], [valueObject, valueObject2]) == actual

    The above assertion will verify that the actual object has two keys where one key contains
    'myplugin.thing' and the other contains 'myplugin.thing2', and that the actual object has two
    values are respectively equal to valueObject and valueObject2.
    '''

    def __init__(self, expected_names: Union[List[str], str],
                 expected_output: List[Dict[str, Any]]) -> None:
        self.expected_output = expected_output
        self.expected_names = expected_names if isinstance(
            expected_names, list) else [expected_names]

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, dict)
        PlumaOutputMatcher._test_output_names_match(self.expected_names, o)
        PlumaOutputMatcher._test_output_values_match(self.expected_output, o)
        return True

    def matches(self, o: object) -> bool:
        return self == o

    @staticmethod
    def _test_output_names_match(expected_keys: List[str],
                                 actual_output: Dict[str, Dict[str, Any]]):
        expected_keys_not_found = list(expected_keys)

        for actual_key in actual_output.keys():
            # verify that the actual name matches at least one of the names in the expected list
            name_matches = [exp_key for exp_key in expected_keys_not_found
                            if exp_key in actual_key]
            if len(name_matches) == 0:
                raise AssertionError(
                    f'Did not find an match for actual key "{actual_key}" '
                    f'in expected keys [{", ".join(expected_keys)}]')
            expected_keys_not_found.remove(name_matches[0])
        if len(expected_keys_not_found) > 0:
            raise AssertionError(
                'Found no match for expected key(s) '
                f'[{", ".join(expected_keys_not_found)}]')

    @staticmethod
    def _test_output_values_match(expected_output: List[Dict[str, Any]],
                                  actual_output: Dict[str, Dict[str, Any]]):
        expected_output_not_found = list(expected_output)
        for key, actual_val in actual_output.items():
            # verify that the actual value matches at least one of values in the expected list
            try:
                found_index = expected_output_not_found.index(actual_val)
            except ValueError:
                raise AssertionError(f'Did not find an match for key {key}')
            else:
                expected_output_not_found.pop(found_index)
        if len(expected_output_not_found) > 0:
            raise AssertionError(
                f'Found too few entries in the actual (expected {len(expected_output)}, '
                f'got {len(actual_output)}')
