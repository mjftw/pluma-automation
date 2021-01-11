from typing import Dict, Optional, List, Type, cast

from pluma import Board
from pluma.cli import DeviceActionBase


class DeviceActionRegistry():
    action_classes_dict: Dict[str, Type[DeviceActionBase]] = {}

    @classmethod
    def register(cls, action_key: str):
        def decorator(action_class: Type[DeviceActionBase]):
            cls.register_class(action_class=action_class,
                               action_key=action_key)
            return action_class
        return decorator

    @classmethod
    def register_class(cls, action_class: Type[DeviceActionBase], action_key: str):
        '''Register a class as DeviceAction, usable from the tests configuration file.'''
        if not issubclass(action_class, DeviceActionBase):
            raise Exception(
                f'Error trying to register Action class "{cast(Type, action_class).__name__}" '
                'which does not inherit DeviceActionBase')

        if action_key in cls.action_classes_dict:
            raise Exception(
                f'Error registering DeviceAction subclass "{action_class}": '
                f'Action key {action_key} is already'
                f' registered for {cls.action_classes_dict[action_key].__name__}')

        cls.action_classes_dict[action_key] = action_class

    @classmethod
    def all_actions(cls) -> List[str]:
        return list(cls.action_classes_dict.keys())

    @classmethod
    def create(cls, board: Board, action: str, args: Optional[dict] = None):
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
                f'Invalid device action command "{action}". '
                f'Supported commands: {cls.all_actions()}')

        aclass = cls.action_class(action)
        if not aclass:
            raise Exception(f'Missing class for device action {action}')

        return aclass(board, **args)

    @classmethod
    def action_class(cls, action_key: str) -> Type[DeviceActionBase]:
        '''Return the class associated with an action string'''
        action_class = cls.action_classes_dict.get(action_key)
        if not action_class:
            raise Exception(f'No action class exists for key "{action_key}"')

        return action_class
