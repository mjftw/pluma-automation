import time

from farmcore.usb_relay import USBRelay
# import farmcore.interact
# from farmcore.board import Board

relay = USBRelay('/dev/ttyUSB1')
# paladin = Board('paladin', None, '3-3.2', None)

def power(state):
    if state not in ['on', 'off']:
        print("Error: power must be 'on' or 'off'")

    if state == 'on':
        print("Power on")
        relay.toggle(1, 'A')
        relay.toggle(2, 'B')
        time.sleep(0.1)

        relay.toggle(2, 'A')
        time.sleep(0.1)
        relay.toggle(2, 'B')

    if state == 'off':
        print("Power off")
        relay.toggle(1, 'B')
        relay.toggle(2, 'B')

def main():
    power('off')
    time.sleep(1)
    power('on')

if __name__ == '__main__':
    main()