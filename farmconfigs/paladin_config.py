from farmcore import farm

relay = farm.USBRelay('/dev/ttyUSB1')
paladin = farm.Board('paladin', None, '3-3.2', None)
