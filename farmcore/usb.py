#!/usr/bin/env python3

import sys
import os
import time
import subprocess

import pyudev

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
        self.usb_device = device

    @property
    def is_bound(self):
        return os.path.isdir(os.path.join(driver_path, self.usb_device))

    def unbind(self):
        if not self.is_bound:
            return
        with open(os.path.join(driver_path, 'unbind'), 'w') as fd:
            fd.write(self.usb_device)
        time.sleep(1)

    def bind(self):
        if self.is_bound:
            return
        with open(os.path.join(driver_path, 'bind'), 'w') as fd:
            fd.write(self.usb_device)
        time.sleep(1)

    def rebind(self):
        self.unbind()
        self.bind()

    def get_device(self):
        try:
            for _ in range(20):
                d = pyudev.Devices.from_path(
                    self.puctx, '/bus/usb/devices/{}'.format(self.usb_device))
                if d is not None:
                    break
                time.sleep(1)
        except:
            raise NoDevice("No device for [{}]".format(self.usb_device))
        return d

    @property
    def child_info(self):
        parent = self.get_device()
        children = self.puctx.list_devices(parent=parent)
        infolist = []

        for child in children:
            devinfo = {}
            devinfo['devnode'] = child.device_node
            if devinfo['devnode'] is None:
                continue

            devinfo['subsystem'] = child.subsystem
            devinfo['vendor'] = child.get('ID_VENDOR')

            devinfo['devtype'] = child.get('DEVTYPE')
            if(devinfo['devtype'] == 'disk' or
               devinfo['devtype'] == 'partition'):
                devinfo['size'] = int(child.attributes.get('size'))

            infolist.append(devinfo)

        return infolist

    def filter_child_info(self, filters={}, excludes={}):
        match_vals = []
        for c in self.child_info:
            match = True
            # Check match list.
            # If the child queried DOES NOT HAVE the required
            # field, OR the field HAS A DIFFERENT value, do not match
            for k, v in filters.items():
                if not match:
                    break
                if k not in c or c[k] != v:
                    match = False

            # Check exclude list
            # If the child queried HAS the required filed AND
            # the field has the SAME VALUE, do not match
            for k, v in excludes.items():
                if not match:
                    break
                if k in c and c[k] == v:
                    match = False

            if match:
                match_vals.append(c)

        return match_vals

    def get_serial(self):
        devinfo = self.filter_child_info({
            'subsystem': 'tty'
        })
        if not devinfo:
            raise NoDevice('No serial devices on {}'.format(self.usb_device))
        else:
            return devinfo[0]['devnode']

    def get_sdmux(self):
        devinfo = self.filter_child_info({
            'subsystem': 'tty',
            'vendor': 'DLP_Design'
        })
        if not devinfo:
            raise IOError('No sdmux devices on {}'.format(self.usb_device))
        else:
            return devinfo[0]['devnode']

    def get_block(self):
        devinfo = self.filter_child_info({
            'subsystem': 'block',
            'devtype': 'disk'
        }, {
            'size': 0
        })
        if not devinfo:
            raise NoDisks('No block devices on {}'.format(self.usb_device))
        else:
            return (devinfo[0]['devnode'], devinfo[0]['size'])

    def get_part(self):
        devinfo = self.filter_child_info({
            'subsystem': 'block',
            'devtype': 'partition'
        }, {
            'size': 0
        })
        if not devinfo:
            raise NoPartitions('No partitions on {}'.format(self.usb_device))
        else:
            return (devinfo[0]['devnode'], devinfo[0]['size'])

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

    def rebind_host(self):
        d = self.get_device()
        if d is None:
            return None

        # Keep going until we find no more parents
        while d.parent:
            d = d.parent

        driver_path = "{}/driver".format(d.sys_path)
        driver_path = os.path.realpath(driver_path)

        print("WARN: Rebinding HOST {} at {}".format(d.sys_name, driver_path))

        subprocess.run(['sudo', 'chmod', 'a+w', driver_path + "/unbind"])
        subprocess.run(['sudo', 'chmod', 'a+w', driver_path + "/bind"])

        with open("{}/unbind".format(driver_path), 'w') as f:
            f.write(d.sys_name)

        time.sleep(2)
        with open("{}/bind".format(driver_path), 'w') as f:
            f.write(d.sys_name)


    #find_block()
    #find_serial()
