import os
import json


HARDWARE_CONF = os.path.join(
    os.path.dirname(
        os.path.realpath(__file__)
    ),
    'hardware.json'
)


class ValidationError(Exception):
    pass


def read_config():
    with open(HARDWARE_CONF, 'r') as f:
        return json.load(f)


def check_schema(obj: dict, schema: dict):
    ''' Check a dict $obj matches the template $schema

    The schema should contain a dictionary tree for obj to be validated
    against. This tree can contain keys and types to check.
    E.g.
    schema = {
        "foo": {
            "bar": {
                "baz": int
            }
        }
    }

    If an dict missing "foo"."bar" was passed in as obj, a ValidationError
    would be raised.
    A ValiationError would also be raised if "foo"."bar"."baz" was not of
    type int.
    '''
    if not isinstance(obj, dict):
        raise AttributeError('obj must be a dict')
    if not isinstance(schema, dict):
        raise AttributeError('schema must be a dict')

    _check_schema_branch(obj, schema, '/')

    return True


def _check_schema_branch(obj, schema, path):
    for key, val in schema.items():
        if key not in obj:
            raise ValidationError(f'Missing key: "{path}.{key}""')
        elif isinstance(val, dict):
            _check_schema_branch(obj[key], val, f'{path}.{key}')
        elif isinstance(val, type):
            if not isinstance(obj[key], val):
                raise ValidationError(f'Incorrect type for "{path}.{key}" Expected {val.__name__}, found {obj[key].__class__.__name__}')
