
import os,sys
from farmcore.farm_base import FarmBase
from farmcore.farm_board import FarmBoard
from farmcore import usb,farm
from importlib import import_module

boards = []

class NoBoard(Exception):
    pass

class Board(FarmBase):
    def __init__(self, name, apc_port, hub, sdm):
        self.apc, self.apc_index = apc_port
        self.hub = hub
        self.sdm = sdm
        self.name = name
        self.log("Registered board at {}".format(hub))
        boards.append(self)

    def __repr__(self):
        return "Board-{}".format(self.name)

    def on(self):
        self.log("PWR On")
        return self.apc.on(self.apc_index)
    
    def off(self):
        self.log("PWR Off")
        return self.apc.off(self.apc_index)

    def use(self, *a, **kw):
        return FarmBoard( self, *a, **kw )

def get_board(name):

    if not boards:
        cfg = os.environ.get('FARMCFG',None)
        if cfg:
            print("We have a config. It is {}".format( cfg ))
            fp = os.path.dirname(os.path.abspath(cfg))
            tld_rel = "{}/..".format( fp )
            tld = os.path.realpath( tld_rel ) 
            sys.path.append( tld )
            import_module(os.path.basename(cfg))
        else:
            raise NoBoard

    for b in boards:
        if b.name == name:
            return b

    raise NoBoard("Can't find board called [{}]".format(name))


def get_name(hub):
    for b in boards:
        if b.hub == hub:
            return b.name

    return None

def get(name, *a, **kw):
    b = get_board(name)
    print("{}".format(b))
    return farm.farm(b, *a, **kw)

def show_info(board):
    usbee = usb.usb()
    ud = board.hub

    print("\n =============== Device [{} - {}] =============".format(
        ud, get_name(ud)))
    d = usbee.get_device(ud)
    for m in usbee.puc.list_devices(
            subsystem='block', DEVTYPE='disk', parent=d):
        if int(m.attributes.get('size')) == 0:
            continue
        print("Block device {} has size {:4.2f}MB".format(
            m.device_node,
            int(m.attributes.get('size')) / (1024 * 1024)))
        usbp = m.find_parent('usb', device_type='usb_device')
        print(" Parent is: {} , {}".format(
            usbp.sys_name, usbp.device_type))
    for m in usbee.puc.list_devices(subsystem='tty', parent=d):
        print(m.device_node, m['ID_VENDOR'])



