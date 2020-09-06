import sys
import os
import pkgutil
import importlib

import pluma.plugins


def load_plugin_modules(module_dir: str):
    if not os.path.isdir(module_dir):
        raise AttributeError(
            f'Cannot import module at {module_dir}, no such directory')

    modules = pkgutil.iter_modules([module_dir])

    if modules:
        sys.path.insert(0, module_dir)
        for module in modules:
            setattr(pluma.plugins, module.name, importlib.import_module(module.name))
    else:
        raise ImportError(f'No modules found at {module_dir}')
