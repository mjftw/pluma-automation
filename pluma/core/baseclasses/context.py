from dataclasses import dataclass


@dataclass
class Credentials:
    '''Data class containing credentials'''
    login: str = None
    password: str = None


@dataclass
class SystemContext:
    '''Data class holding system related configuration'''
    prompt_regex: str = r'\$'
    credentials: Credentials = Credentials()
