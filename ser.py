#!/usr/bin/env python3

import sys,os
import usb
import boards

sport = usb.usb().get_serial(boards.get_board(sys.argv[1]).hub)

screen_bin='/usr/bin/screen'

os.execl(screen_bin, screen_bin, sport, '115200')