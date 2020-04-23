import re


class ValidationError(Exception):
    pass


def check_schema(obj: dict, schema: dict):
    ''' Check a dict $obj matches the template $schema

    The schema should contain a dictionary tree for obj to be validated
    against. This tree can contain keys match and value checks.
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
    In this case the check for "foo"."bar"."baz" was a type check.

    A regex check could also be done:
    E.g.
    schema = {
        "foo": {
            "bar": {
                "baz": re.compile(r'[0-9]')
            }
        }
    }

    If the value of "foo"."bar"."baz" did not match the regex pattern '[0-9]'
    the a ValidationError would be raised.
    This uses the Pattern class from the builtin module re.

    If no value checking is required, set the check to None.
    E.g.
    schema = {
        "foo": {
            "bar": {
                "baz": None
            }
        }
    }
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
        elif isinstance(val, re.Pattern):
            if not val.fullmatch(obj[key]):
                raise ValidationError(f'"{path}.{key}" did not match expected regex: {val.pattern}')
        elif isinstance(val, type):
            if not isinstance(obj[key], val):
                raise ValidationError(f'Incorrect type for "{path}.{key}" Expected {val.__name__}, found {obj[key].__class__.__name__}')
