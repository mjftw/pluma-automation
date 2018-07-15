#!/usr/bin/env python3

import sys
import os
import stat
import time
from pprint import pprint as pp
import subprocess as sp
import pyudev
import board

driver_path = '/sys/bus/usb/drivers/usb/'


class NoPartitions(Exception):
    pass


class NoDisks(Exception):
    pass


class NoDevice(Exception):
    pass


class USB():
    def __init__(self, device):
        self.puctx = pyudev.Context()
        self.device = device

    @property
    def is_bound(self):
        return os.path.isdir(os.path.join(driver_path, self.device))

    def _get_dev(self):
        try:
            for _ in range(20):
                d = pyudev.Devices.from_path(
                    self.puctx, '/bus/usb/devices/{}'.format(self.device))
                if d is not None:
                    break
                time.sleep(1)
        except:
            raise NoDevice("No device for [{}]".format(self.device))
        return d

    def unbind(self):
        if not self.is_bound:
            return
        with open(os.path.join(driver_path, 'unbind'), 'w') as fd:
            fd.write(self.device)
        time.sleep(1)

    def bind(self):
        if self.is_bound:
            return
        with open(os.path.join(driver_path, 'bind'), 'w') as fd:
            fd.write(self.device)
        time.sleep(1)

    def rebind(self):
        self.unbind()
        self.bind()

    def get_devnode(self, subsys, devtype=None, vendor_id=None, attempts=1):
        """ Find the device node for the first device matches """
        dev = self._get_dev()
        for _ in range(attempts):
            if devtype is not None:
                devices = self.puctx.list_devices(
                    subsystem=subsys, DEVTYPE=devtype, parent=dev)
            else:
                devices = self.puctx.list_devices(
                    subsystem=subsys, parent=dev)
            for m in devices:
                if(vendor_id is not None and
                        (m.get('ID_VENDOR') is None or
                            m['ID_VENDOR'] != vendor_id)):
                    continue
                if(subsys == 'block' and
                        int(m.attributes.get('size')) == 0):
                    continue
                return m.device_node
            if attempts != 1:
                time.sleep(1)
        return None

    def get_block(self):
        """ Wrapper for get_devnode for block devices"""
        devnode = self.get_devnode(
            subsys='block', devtype='disk', attempts=10)
        if devnode is None:
            raise NoDisks('No block devices on {}'.format(self.device))
        else:
            return devnode

    # Get first partition name for block device
    def get_part(self):
        """ Wrapper for get_devnode for disk partitions"""
        devnode = self.get_devnode(
            subsys='block', devtype='partition', attempts=5)
        if devnode is None:
            raise NoPartitions('No partitions on {}'.format(self.device))
        else:
            return devnode

    def get_tty(self):
        """ Wrapper for get_devnode for tty devices"""
        devnode = self.get_devnode(
            subsys='tty', attempts=5)
        if devnode is None:
            raise NoDevice('No tty devices on {}'.format(self.device))
        else:
            return devnode

    def show_ancestry(self):
        dev = self._get_dev()

        while d.parent:
            p = dev.parent
            print(dir(p))
            print(p.driver, p.subsystem, p.sys_name, p.device_path, p.sys_path)
            sp.run(['ls', "{}/driver".format(p.sys_path)])
            dev = p

    def rebind_host(self):
        dev = self._get_dev

        # Keep going until we find no more parents
        while dev.parent:
            dev = dev.parent

        path = os.path.join(dev.sys_path, 'driver')
        path = os.path.realpath(path)

        # print("WARN: Rebinding HOST {} at {}".format(dev.sys_name, self.get_driver_path()))
        unbind_path = os.path.join(driver_path, 'unbind')
        bind_path = os.path.join(driver_path, 'bind')

        os.chmod(unbind_path, stat.S_IWOTH)
        os.chmod(bind_path, stat.S_IWOTH)

        with open(unbind_path, 'w') as fd:
            f.write(dev.sys_name)

        time.sleep(2)
        with open(bind_path, 'w') as fd:
            f.write(dev.sys_name)

#find_block( device )
#find_serial( device )
