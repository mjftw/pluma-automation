#!/usr/bin/env python3

import sys
import os
import time
from pprint import pprint as pp
import subprocess as sp
import pyudev as pu
import board

bind_path = "/sys/bus/usb/drivers/usb/bind"
unbind_path = "/sys/bus/usb/drivers/usb/unbind"


class NoPartitions(Exception):
    pass


class NoDisks(Exception):
    pass


class NoDevice(Exception):
    pass


class USB():
    def __init__(self, usb_device):
        self.puc = pu.Context()
        self.usb_device = usb_device

    def __repr__(self):
        return "\n[USB: usb_device={}]".format(self.usb_device)

    def unbind(self):
        try:
            #print("unbinding {}".format( self.usb_device ) )
            device = self.get_device()
            if device is None:
                return
            d = os.path.basename(device['DEVPATH'])
            unbind_fd = open(unbind_path, 'w')
            unbind_fd.write(d)
            unbind_fd.close()
        except:
            #print("No device to unbind, lets carry on")
            pass
        time.sleep(1)

    def bind(self):
        #print("binding {}".format( self.usb_device ) )
        device = self.get_device()
        d = os.path.basename(device['DEVPATH'])
        bind_fd = open(bind_path, 'w')
        bind_fd.write(d)
        bind_fd.close()
        time.sleep(1)

    def rebind(self):
        self.unbind(self.usb_device)
        self.bind(self.usb_device)

    def get_device(self):
        #print("Looking for device {}".format( self.usb_device ))
        try:
            for _ in range(20):
                d = pu.Devices.from_path(
                    self.puc, '/bus/usb/devices/{}'.format(self.usb_device))
                if d is not None:
                    break
                time.sleep(1)
        except:
            raise NoDevice("No device for [{}]".format(self.usb_device))
        return d

    def get_serial(self):
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for serial devicces on [{}]".format( self.usb_device ))
        for _ in range(20):
            for m in self.puc.list_devices(subsystem='tty', parent=d):
                #print("Found serial {}".format( m.device_node ))
                return m.device_node
            time.sleep(2)
        raise IOError('No serial devices on '.format(self.usb_device))

    def get_sdmux(self):
        sdmux_id = 'DLP_Design'
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for sdmux devicces on [{}]".format( self.usb_device ))
        for _ in range(20):
            for m in self.puc.list_devices(subsystem='tty',  parent=d):
                if m.get('ID_VENDOR') is None:
                    continue
                if m['ID_VENDOR'] == sdmux_id:
                    #print("Found sdmux as {}".format( m.device_node ))
                    return m.device_node
            time.sleep(2)
        raise IOError('No sdmux devices on '.format(self.usb_device))

    # Return the device node and the sysname for the usb parent for use with the bind/unbind
    def get_block(self):
        d = self.get_device()
        if d is None:
            return None
        #print("Searching for block devicces on [{}]".format( self.usb_device ))
        for _ in range(20):
            blks = self.puc.list_devices(
                subsystem='block',  DEVTYPE='disk', parent=d)
            for m in blks:
                if int(m.attributes.get('size')) == 0:
                    continue
                #print("Block device {} has size {:4.2f}MB".format(
                #    m.device_node,
                #    int(m.attributes.get('size')) / 1024 / 1024 ))
                usbp = m.find_parent('usb', device_type='self.usb_device')
                #print(" Parent is: {} , {}".format( usbp.sys_name, usbp.device_type ))
                return(m.device_node, usbp.sys_name)
            time.sleep(2)
        raise NoDisks('No block devices on {}'.format(self.usb_device))

    # Get first partition name for block device
    def get_part(self):
        d = self.get_device()
        if d is None:
            raise NoDevice("No device for {}".format(self.usb_device))
        #print("Searching for block devicces on [{}]".format( self.usb_device ))
        for _ in range(5):
            blks = self.puc.list_devices(
                subsystem='block',  DEVTYPE='partition', parent=d)
            for m in blks:
                if int(m.attributes.get('size')) == 0: continue
                #print("Block device {} has size {:4.2f}MB".format(
                #    m.device_node,
                #    int(m.attributes.get('size')) / 1024 / 1024 ))
                #usbp = m.find_parent('usb', device_type='self.usb_device')
                #print(" Parent is: {} , {}".format( usbp.sys_name, usbp.device_type ))
                return m.device_node
            time.sleep(2)
        raise NoPartitions('No partitions on {}'.format(self.usb_device))

    def show_ancestry(self):
        d = self.get_device()
        if d is None:
            return None

        while d.parent:
            p = d.parent
            print(dir(p))
            print(p.driver, p.subsystem, p.sys_name, p.device_path, p.sys_path)
            sp.run(['ls', "{}/driver".format(p.sys_path)])
            d = p

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

        sp.run(['sudo', 'chmod', 'a+w', driver_path + "/unbind"])
        sp.run(['sudo', 'chmod', 'a+w', driver_path + "/bind"])

        with open("{}/unbind".format(driver_path), 'w') as f:
            f.write(d.sys_name)

        time.sleep(2)
        with open("{}/bind".format(driver_path), 'w') as f:
            f.write(d.sys_name)


def show_info(boards):
    _usb = USB(usb_device=[])

    for b in boards:
        _usb.usb_device.append(b.hub.usb)

    for ud in _usb.usb_device:
        print("\n =============== Device [{} - {}] =============".format(
            ud, board.get_name(boards, ud)))
        d = _usb.get_device()
        if d is None:
            continue
        for m in _usb.puc.list_devices(
                subsystem='block', DEVTYPE='disk', parent=d):
            if int(m.attributes.get('size')) == 0:
                continue
            print("Block device {} has size {:4.2f}MB".format(
                m.device_node,
                int(m.attributes.get('size')) / (1024 * 1024)))
            usbp = m.find_parent('usb', device_type='usb_device')
            print(" Parent is: {} , {}".format(
                usbp.sys_name, usbp.device_type))
        for m in _usb.puc.list_devices(subsystem='tty', parent=d):
            print(m.device_node, m['ID_VENDOR'])

#find_block( usb_device )
#find_serial( usb_device )
