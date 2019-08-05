def getch():
    '''
    Get a single character from stdin and return it.
    Function blocks until character recieved.
    '''
    from sys import stdin
    from tty import setraw
    from termios import tcgetattr, tcsetattr, TCSADRAIN

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
    from curses.ascii import unctrl

    key = None
    keyhex = None
    print('Echoing key values. Press Ctrl-C to exit')
    while keyhex != b'\x03':
        key = getch()
        keyhex = key.encode(encoding)
        print(f'Pressed: {unctrl(key)} Hex: {keyhex}')
