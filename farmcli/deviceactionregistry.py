import re

from farmcore import Board
from farmcli import DeviceActionBase


class DeviceActionRegistry():
    action_classes_dict = {}

    @classmethod
    def register(cls, action_key: str = None):
        def decorator(action_class: DeviceActionBase):
            cls.register_class(action_class=action_class,
                               action_key=action_key)
            return action_class
        return decorator

    @classmethod
    def register_class(cls, action_class: DeviceActionBase, action_key: str = None):
        '''Register a class as DeviceAction, usable from the tests configuration file.

        The "action_key" defaults to the name of the class stripped from "Action", lower case.'''
        if not action_key:
            action_key = re.sub(r'Action$', '', action_class.__name__).lower()

        if not issubclass(action_class, DeviceActionBase):
            raise Exception(
                f'Error trying to register Action class "{action_class.__name__}" which does not inherit DeviceActionBase')

        if action_key in cls.action_classes_dict:
            raise Exception(
                f'Error registering DeviceAction subclass "{action_class}": Action key {action_key} is already'
                ' registered for {cls.action_classes_dict[action_key].__name__}')

        cls.action_classes_dict[action_key] = action_class

    @classmethod
    def all_actions(cls):
        return cls.action_classes_dict.keys()

    @classmethod
    def create(cls, board: Board, action: str, args: dict = None):
        if not action or not isinstance(action, str):
            raise ValueError(
                f'Invalid device action "{action}": Actions must be a single string')

        if not args:
            args = {}

        if not isinstance(args, dict):
            raise ValueError(
                f'Invalid device action arguments "{args}": Arguments must be a dict')

        if action not in cls.action_classes_dict:
            raise ValueError(
                f'Invalid device action command "{action}". Supported commands: {cls.all_actions()}')

        aclass = cls.action_class(action)
        if not aclass:
            raise Exception(f'Missing class for device action {action}')

        return aclass(board, **args)

    @classmethod
    def action_class(cls, action_key: str) -> type:
        '''Return the class associated with an action string'''
        return cls.action_classes_dict.get(action_key)
