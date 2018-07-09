#!/usr/bin/env python3

import boards
import sys

b = boards.get(sys.argv[1], logfile=None)
b.init()

b.board()
b.on()
