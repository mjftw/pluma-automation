import re

from .config import ConfigPreprocessor


class PlumaConfigPreprocessor(ConfigPreprocessor):
    def __init__(self, variables: dict):
        self.variables = variables

    def preprocess(self, raw_config: str) -> str:
        def token_to_variable(token):
            '''remove "${" and "}" '''
            return token[2:len(token)-1]

        missing_variables = []
        vars_found = re.findall(r'\${\w+}', raw_config, flags=re.MULTILINE)
        unique_vars = set(map(token_to_variable, vars_found))
        vars_found = map(token_to_variable, vars_found)

        # Look for missing variables
        for variable in unique_vars:
            if variable not in self.variables:
                missing_variables.append(variable)

        if missing_variables:
            raise Exception('The following variables are used but not defined: '
                            f'{missing_variables}')

        for variable in unique_vars:
            raw_config = re.sub(r'\${'+variable+'}', self.variables[variable],
                                raw_config)

        return raw_config
