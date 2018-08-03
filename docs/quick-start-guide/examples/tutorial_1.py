"""
Tutorial example 1:
    - How the hardware configuration of a farm is
      represented in software
"""

"""
The farmcore package includes the definitions of all farm hardware classes
"""
from farmcore import farm

"""
Each PDU in the farm is given a PDU class instance.
The PDU uses the telnet protocol, so PDU class takes arguments for it's IP
address, and the telnet user login details to be used.
"""
pdu1 = farm.PDU(host='10.103.3.40', user='apc', pw='apc')

"""
Each USB Relay in the farm is given a USBRelay class instance.
The only argument required is the usb device path of the relay.
"""
ur1 = farm.USBRelay(usbpath='1-1.1.4.1')
ur2 = farm.USBRelay(usbpath='1-1.1.4.3')

"""
Each SD Mux in the farm is given an SDMux class instance.
The SD Mux is physically connected a USB Relay, and a PDU.
Each class instance is therefore given a reference to these.
"""
sdm1 = farm.SDMux(ur_port=ur2[0], pdu_port=pdu1[2])
sdm2 = farm.SDMux(ur_port=ur2[3], pdu_port=pdu1[1])
sdm3 = farm.SDMux(ur_port=ur2[2], pdu_port=pdu1[3])

"""
Each board in the farm is represented and controlled by an instance of the
Board class.
In order for a board to be uniquely identified, it is given a name.
Each board is physically connected a PDU, SD Mux, and its Board Hub.
Each class instance is therefore given a reference to these.
"""
bbb  = farm.Board(name='bbb',  pdu_port=pdu1[7], hub='1-1.1.1', sdmux=sdm1)
fb42 = farm.Board(name='fb42', pdu_port=pdu1[4], hub='1-1.1.2', sdmux=sdm2)
fb43 = farm.Board(name='fb43', pdu_port=pdu1[6], hub='1-1.1.3', sdmux=sdm3)
