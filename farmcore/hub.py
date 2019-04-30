import re

from .farmclass import Farmclass
from .usb import USB, puctx


class Hub(Farmclass, USB):
    def __init__(self, usb_device):
        USB.__init__(self, usb_device)

    @property
    def devinfo(self):
        return self._pack_devinfo(self.get_device())

    @property
    def downstream(self):
        infolist = []

        downstream_devs = puctx.list_devices(
            parent=self.get_device())

        for dev in downstream_devs:
            info = self._pack_devinfo(dev)
            if info:
                infolist.append(self._pack_devinfo(dev))

        return infolist

    def _pack_devinfo(self, device):
        devinfo = {}
        if device.device_node is None:
            return devinfo
        else:
            devinfo['devnode'] = device.device_node

        pattern = re.compile(self.usb_device + r'[0-9.-]*')
        devinfo['usbpath'] = pattern.findall(device.device_path)[-1]

        devinfo['subsystem'] = device.subsystem
        devinfo['vendor'] = device.get('ID_VENDOR')
        devinfo['major'] = device.get('MAJOR')
        devinfo['minor'] = device.get('MINOR')

        devinfo['devtype'] = device.get('DEVTYPE')
        if(devinfo['devtype'] == 'disk' or
           devinfo['devtype'] == 'partition'):
            devinfo['size'] = int(device.attributes.get('size'))

        return devinfo

    def filter_downstream(self, filters={}, excludes={}):
        return self._filter_dictarr(
            filters=filters, excludes=excludes, dictarr=self.downstream)

    def _filter_dictarr(self, filters={}, excludes={}, dictarr=[{}]):
        match_vals = []
        for d in dictarr:
            match = True
            # Check match list.
            # If the dict array queried DOES NOT HAVE the required
            # field, OR the field HAS A DIFFERENT value, do not match
            for k, v in filters.items():
                if not match:
                    break
                if k not in d or d[k] != v:
                    match = False

            # Check exclude list
            # If the dict array queried HAS the required filed AND
            # the field has the SAME VALUE, do not match
            for k, v in excludes.items():
                if not match:
                    break
                if k in d and d[k] == v:
                    match = False

            if match:
                match_vals.append(d)

        return match_vals

    def get_serial(self, key=None):
        ttyUSB_major = '188'
        devinfo = self.filter_downstream({
            'subsystem': 'tty',
            'major': ttyUSB_major,
            'vendor': 'FTDI'
        })

        if not devinfo:
            None
        else:
            if key:
                return devinfo[0][key]
            else:
                return devinfo[0]

    def get_relay(self, key=None):
        devinfo = self.filter_downstream({
            'subsystem': 'tty',
            'vendor': 'DLP_Design'
        })
        if not devinfo:
            devinfo = self.filter_downstream({
                'vendor': 'DLP_Design'
            })

        if not devinfo:
            None
        else:
            if key:
                return devinfo[0][key]
            else:
                return devinfo[0]

    def get_block(self, key=None):
        devinfo = self.filter_downstream({
            'subsystem': 'block',
            'devtype': 'disk'
        }, {
            'size': 0
        })
        if not devinfo:
            None
        else:
            return devinfo[0]

    def get_part(self, key=None):
        devinfo = self.filter_downstream({
            'subsystem': 'block',
            'devtype': 'partition'
        }, {
            'size': 0
        })
        if not devinfo:
            None
        else:
            if key:
                return devinfo[0][key]
            else:
                return devinfo[0]

    #TODO: Add a get_usbether() method

    def get_parent(self):
        dev = self.get_device()
        pdev = dev.find_parent(subsystem='usb', device_type='usb_device')
        return pdev.sys_name

    def show_ancestry(self):
        dev = self.get_device()
        if dev is None:
            return None

        while dev.parent:
            p = dev.parent
            print(dir(p))
            print(p.driver, p.subsystem, p.sys_name, p.device_path, p.sys_path)
            subprocess.run(['ls', "{}/driver".format(p.sys_path)])
            dev = p
