import sys
import os
import pkgutil
import importlib


def load_modules(module_dir: str):
    if not os.path.isdir(module_dir):
        raise AttributeError(
            f'Cannot import module at {module_dir}, no such directory')

    modules = pkgutil.iter_modules([module_dir])

    if modules:
        sys.path.insert(0, module_dir)
        for module in modules:
            importlib.import_module(module.name)
    else:
        raise ImportError(f'No modules found at {module_dir}')

    print(modules)
