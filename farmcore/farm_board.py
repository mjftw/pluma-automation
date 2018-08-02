
import sys,os
import time
import serial
import pexpect
import subprocess as sp
import getpass
from farmcore import usb, interact
from farmcore.farm_base import FarmBase

DEFAULT_LOGFILE = object()

class FarmBoard(FarmBase):
    def __init__(self, 
            board, 
            logfile=DEFAULT_LOGFILE, 
            blogfile=DEFAULT_LOGFILE, 
            mount_path = None,
            bootline = None ):
        self.brd = board
        self.hub = board.hub
        self.usb = usb.USB(board.hub)
        self.disk = None
        self.diskusb = None
        self._p = None
        self._s = None
        
        self.log("Creating FarmBoard instance for board {}".format( self.brd ))

        self.logfile = logfile
        self.blogfile = blogfile

        if logfile == DEFAULT_LOGFILE:
            self.logfile = open("/tmp/user_{}_{}.log".format(board.name, getpass.getuser() ), "ab")

        if blogfile == DEFAULT_LOGFILE:
            self.blogfile = open("/tmp/board_{}_{}.log".format(board.name, getpass.getuser() ), "ab")
        elif blogfile is None:
            self.blogfile = sys.stdout.buffer

        if mount_path is None:
            self.mount_path = '/tmp/mount_{}'.format(self.brd.name)
        else:
            self.mount_path = mount_path

        try:
            os.mkdir(self.mount_path)
        except FileExistsError:
            self.log("Mount path {} already exists".format(self.mount_path))

        cmd = 'sudo umount {path}'.format(path = self.mount_path)
        while sp.run( cmd.split() ).returncode == 0:
            self.log("WARN: Mount path had mount on it. Unmounted it.")
            pass
        
        self.clog("LOG[{}] BLOG[{}]".format(self.logfile, self.blogfile))

    def __repr__(self):
        return "FB-{}".format(self.brd)


    def init(self):
        self.log("Initialising board [{}]".format(self.brd))
        self._p = None

        # If we find a disk at start of day, we must try to ensure it
        # isn't mounted!
        try:
            part = self.usb.get_part()
        except usb.NoPartitions:
            # We need to run through the full init now.
            pass
        else:
            # We have a disk so let's not muck around too much.
            self.log("WARN: Disk found {} at init, attempting unmount.".format(part))
            cmd = 'sudo umount {device}'.format(device=part)
            sp.run(cmd.split())

        # We have to turn the boards off
        self.off()

        self.log("Power cycle the sdmux...")
        self.brd.sdm.off()
        time.sleep(8)
        self.brd.sdm.on()

        self.log("Rebinding whole HUB...")
        self.usb.rebind(self.hub)

        self._host()

        self.log(str(self.p))

        try:
            part = self.diskusb.get_part()
        except usb.NoPartitions:
            self.log("WARNING: Disk at {} has no partitions. May need to format disk".format(self.disk))

        self.log("Disk [{disk}] DiskUsb [{diskusb}] Hub [{hub}] SDMUX [{sdmux}] SERIAL [{serial}]".format(
            disk = self.disk,
            diskusb = self.diskusb,
            hub = self.hub,
            sdmux = self.brd.sdm,
            serial = self.serial
            ))

    @property
    def serial(self):
        return self.usb.get_serial()

    @property
    def p(self):
        if self._p is None:
            self.log("Configuring interact module...")
            for _ in range(10):
                try:
                    self._p = interact.serialSpawn(
                        self.serial, board=self, logfile=self.blogfile)
                except RuntimeError as e:
                    self.log("Failed to init serial [{}], rebooting board.", e)
                    self.off()
                    time.sleep(1)
                    self.on()
                    self._p = None
                else:
                    # Wrappers around interact
                    self.psr = self._p.psr
                    self.send_newline = self._p.send_newline
                    self.send = self._p.send
                    self.waitr = self._p.waitr
                    self.waitre = self._p.waitre
                    self.snr = self._p.snr
                    self.expect = self._p.expect
                    self.echo_off = self._p.echo_off
                    self.wait_for_quiet = self._p.wait_for_quiet
                    return self._p

            self.err('Could not connect to serial.')

        return self._p

    @property
    def default_prompt(self):
        return interact.default_prompt

    def on(self):
        self.log("Power ON")
        return self.brd.on()

    def off(self):
        self.log("Power OFF")
        return self.brd.off()

    def test_disk(self):
        # First we delay until we have permission
        self.log("Test read access to [{}]".format( self.disk))
        for _ in range(10):
            try:
                with open(self.disk, "rb") as f:
                    f.read(1)
            except PermissionError:
                time.sleep(1)
                continue
            except:
                self.log("Error with disk at [{}]".format(self.disk))
                raise
            else:
                return

    def host(self):
        try:
            self._host()
        except:
            self.log("Disk error! Trying to reinit!")
        else:
            return

        try:
            self.init()
        except:
            self.err("Fatal disk error")
        else:
            return

    def _host(self):
        self.log("Switching SD to host...")
        ok = False

        for _ in range(5):
            self.brd.sdm.host()

            if self.diskusb:
                self.usb.rebind(self.diskusb)

            # Sometimes, the disk fails to enumerate
            self.log("Looking for disks...")
            try:
                self.disk, diskusb_dev = self.usb.get_block()
                self.diskusb = usb.USB(diskusb_dev)
            except usb.NoDisks:
                self.log("No disks found yet, retrying...")
                continue

            try:
                self.test_disk()
            except:
                self.log("Disk error on testing, retry.")
                continue

            self.log("DISKUSB at [{}]..".format(self.diskusb))
            return

        raise RuntimeError("Fatal disk error!")

    def board(self):
        self.log("Switching SD to board...")
        self.usb.unbind(self.diskusb)
        self.brd.sdm.board()
        time.sleep(1)

    def unmount(self):
        dev = self.diskusb.get_part()
        self.log("Umounting device {}...".format(dev))
        cmd = 'sudo umount {device}'.format(device=dev)
        sp.run(cmd.split())

    def mount(self):
        uid = os.getuid()
        dev = self.diskusb.get_part()
        self.log("Mounting device {} at {}....".format(dev, self.mount_path))
        cmd = 'sudo mount -o uid={uid} {device} {path}'.format(uid=uid, device=dev, path=self.mount_path)
        sp.run(cmd.split())

    def root(self, path):
        return "{}/{}".format(self.mount_path, path)



