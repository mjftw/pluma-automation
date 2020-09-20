from dataclasses import dataclass

from pluma import Board


@dataclass
class PlumaContext:
    '''Data class for Pluma context'''
    board: Board
    variables: dict
