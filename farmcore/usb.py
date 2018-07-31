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
        self.device = device

    @property
    def is_bound(self):
        return os.path.isdir(os.path.join(driver_path, self.device))

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

    def get_device(self):
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

    def get_serial(self):
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for serial devicces on [{}]".format( usb_device ))
        for _ in range(20):
            for m in self.puctx.list_devices(subsystem='tty', parent=d):
                #print("Found serial {}".format( m.device_node ))
                return m.device_node
            time.sleep(2)
        raise IOError('No serial devices on '.format())

    def get_sdmux(self):
        sdmux_id = 'DLP_Design'
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for sdmux devicces on [{}]".format( self.device ))
        for _ in range(20):
            for m in self.puctx.list_devices(subsystem='tty',  parent=d):
                if m.get('ID_VENDOR') is None:
                    continue
                if m['ID_VENDOR'] == sdmux_id:
                    #print("Found sdmux as {}".format( m.device_node ))
                    return m.device_node
            time.sleep(2)
        raise IOError('No sdmux devices on {}'.format(self.device))

    # Return the device node and the sysname for the usb parent for use with the bind/unbind
    def get_block(self):
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for block devicces on [{}]".format( self.device ))
        for _ in range(20):
            blks = self.puctx.list_devices(
                subsystem='block',  DEVTYPE='disk', parent=d)
            for m in blks:
                if int(m.attributes.get('size')) == 0:
                    continue
                #print("Block device {} has size {:4.2f}MB".format(
                #    m.device_node,
                #    int(m.attributes.get('size')) / 1024 / 1024 ))
                usbp = m.find_parent('usb', device_type='usb_device')
                #print(" Parent is: {} , {}".format( usbp.sys_name, usbp.device_type ))
                return(m.device_node, usbp.sys_name)
            time.sleep(2)
        raise NoDisks('No block devices on {}'.format(self.device))

    # Get first partition name for block device
    def get_part(self):
        d = self.get_device()
        if d is None:
            raise NoDevice("No device for {}".format(self.device))
        #print("Searching for block devicces on [{}]".format( self.device ))
        for _ in range(5):
            blks = self.puctx.list_devices(
                subsystem='block',  DEVTYPE='partition', parent=d)
            for m in blks:
                if int(m.attributes.get('size')) == 0: continue
                #print("Block device {} has size {:4.2f}MB".format(
                #    m.device_node,
                #    int(m.attributes.get('size')) / 1024 / 1024 ))
                #usbp = m.find_parent('usb', device_type='usb_device')
                #print(" Parent is: {} , {}".format( usbp.sys_name, usbp.device_type ))
                return m.device_node
            time.sleep(2)
        raise NoPartitions('No partitions on {}'.format(self.device))

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
