import os
import importlib

for file in os.listdir(os.path.dirname(__file__)):
    mod_name = file[:-3]   # strip .py at the end
    if not mod_name.startswith('__'):
        exec('from .' + mod_name + ' import *')
