'''
This file contains misc blocking functions intended for
use in an interactive interpereter session.
'''

from sys import stdin
from tty import setraw
from termios import tcgetattr, tcsetattr, TCSADRAIN
from curses.ascii import unctrl


def getch():
    '''
    Get a single character from stdin and return it.
    Function blocks until character recieved.
    '''

    fd = stdin.fileno()
    old_settings = tcgetattr(fd)
    setraw(stdin.fileno())

    ch = stdin.read(1)

    tcsetattr(fd, TCSADRAIN, old_settings)

    return ch


def seech(encoding='utf-8'):
    '''
    Print key presses with corresponding hex value.
    Function blocks until Ctrl-C is pressed.
    '''

    key = None
    keyhex = None
    print('Echoing key values. Press Ctrl-C to exit')
    while keyhex != b'\x03':
        key = getch()
        keyhex = key.encode(encoding)
        hex_val = f'0x{keyhex.hex()}'
        int_val = int(hex_val, 16)
        print(f'Pressed: {unctrl(key)} Char: {keyhex} Hex: {hex_val} Int: {int_val}')
