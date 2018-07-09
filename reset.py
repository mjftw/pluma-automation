#!/usr/bin/env python3
from apc.utility import APC
import time
import boards

apc = APC('apc1', 'apc', 'apc', quiet=True)

for sdm in boards.sdms:
    apc.off(sdm.apc, 0)

time.sleep(8)

for sdm in boards.sdms:
    apc.on(sdm.apc, 0)

apc.disconnect()
