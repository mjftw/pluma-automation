from farmclass import Farmclass
from usb import USB


class Hub(Farmclass, USB):
    def __init__(self, usbdev):
        USB.__init__(self, usbdev)

    def get_devices(self):
        dev = USB._get_dev()
        for m in USB.puctx.list_devices(
                subsystem='block', DEVTYPE='disk', parent=dev):
            if int(m.attributes.get('size')) == 0:
                continue
            print("Block device {} has size {:4.2f}MB".format(
                m.device_node,
                int(m.attributes.get('size')) / (1024 * 1024)))
            usbp = m.find_parent('usb', device_type='device')
            if usbp is not None:
                print("Parent is: {}, {}".format(
                    usbp.sys_name, usbp.device_type))
        for m in USB.puctx.list_devices(subsystem='tty', parent=dev):
            print(m.device_node, m['ID_VENDOR'])