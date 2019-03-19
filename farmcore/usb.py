import os
import time
import subprocess

import pyudev

puctx = pyudev.Context()


class NoDevice(Exception):
    pass


class USB():
    driver_path = '/sys/bus/usb/drivers/usb/'

    def __init__(self, device):
        if not hasattr(self, 'usb_device'):
            self.usb_device = device

    def __repr__(self):
        return '{}'.format(self.usb_device)

    @property
    def is_bound(self):
        return os.path.isdir(os.path.join(self.driver_path, self.usb_device))

    def unbind(self):
        if not self.is_bound:
            return
        with open(os.path.join(self.driver_path, 'unbind'), 'w') as fd:
            fd.write(self.usb_device)
        time.sleep(1)

    def bind(self):
        if self.is_bound:
            return
        with open(os.path.join(self.driver_path, 'bind'), 'w') as fd:
            fd.write(self.usb_device)
        time.sleep(1)

    def rebind(self):
        self.unbind()
        self.bind()

    def get_device(self):
        for d in puctx.list_devices(subsystem='usb'):
            if d.device_path.endswith(self.usb_device):
                return d

        raise NoDevice("No device for [{}]".format(self.usb_device))

    def rebind_host(self):
        d = self.get_device()
        if d is None:
            return None

        # Keep going until we find no more parents
        while d.parent:
            d = d.parent

        self.driver_path = "{}/driver".format(d.sys_path)
        self.driver_path = os.path.realpath(self.driver_path)

        print("WARN: Rebinding HOST {} at {}".format(d.sys_name, self.driver_path))

        subprocess.run(['sudo', 'chmod', 'a+w', self.driver_path + "/unbind"])
        subprocess.run(['sudo', 'chmod', 'a+w', self.driver_path + "/bind"])

        with open("{}/unbind".format(self.driver_path), 'w') as f:
            f.write(d.sys_name)

        time.sleep(2)
        with open("{}/bind".format(self.driver_path), 'w') as f:
            f.write(d.sys_name)
