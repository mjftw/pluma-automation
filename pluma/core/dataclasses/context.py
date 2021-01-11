from dataclasses import dataclass
from typing import Optional


@dataclass
class Credentials:
    '''Data class containing credentials'''
    login: str = 'root'
    password: Optional[str] = None


@dataclass
class SystemContext:
    '''Data class holding system related configuration'''
    prompt_regex: Optional[str] = r'\$'
    credentials: Credentials = Credentials()
