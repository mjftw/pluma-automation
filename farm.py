#TODO: import Logger


class Farm():
    def __init__(self, boards):
        self.boards = boards

    def __repr__(self):
        return "Farm: {}".format(self.boards)

    def board_info():
        for b in self.boards:
            ud = b.hub.usb
            print("\n =============== Device [{} - {}] =============".format(
                ud.device, b.name))
            ud.show_info()




# import usb
# import sys
# import os
# import time
# import serial
# import interact
# import pexpect
# from myapc import APC
# import subprocess as sp

# import sdmux

# DEFAULT_LOGFILE = object()

# class farm():
#     def __init__(self, board, logfile=DEFAULT_LOGFILE, blogfile=DEFAULT_LOGFILE, mount_path=None):
#         self.usb = usb.usb()
#         self.brd = board
#         self.apc = board.apc
#         self.sdmux, self.sdmux_index = (board.sdmux.ur.usb, board.sdmux.index)
#         self.hub = board.hub
#         self.disk = None
#         self.diskusb = None
#         self._p = None
#         self._s = None
#         self.logfile = logfile
#         self.blogfile = blogfile

#         if logfile == DEFAULT_LOGFILE:
#             self.logfile = open("/tmp/user_{}.log".format(board.name), "ab")

#         if blogfile == DEFAULT_LOGFILE:
#             self.blogfile = open("/tmp/board_{}.log".format(board.name), "ab")
#         elif blogfile is None:
#             self.blogfile = sys.stdout.buffer

#         if mount_path is None:
#             self.mount_path = '/tmp/mount_{}'.format(self.brd.name)
#         else:
#             self.mount_path = mount_path

#         try:
#             os.mkdir(self.mount_path)
#         except FileExistsError:
#             self.log("Mount path {} already exists".format(self.mount_path))

#         cmd = 'sudo umount {path}'.format(path=self.mount_path)
#         while sp.run(cmd.split()).returncode == 0:
#             self.log("WARN: Mount path had mount on it. Unmounted it.")
#             pass

#         print("LOG[{}]\nBLOG[{}]".format(self.logfile, self.blogfile))

#     def __repr__(self):
#         return "farm({})".format(self.brd.name)

#     def log(self, s):

#         if not isinstance(s, str):
#             s = str(s)

#         # If there IS a logfile, we don't need the prefix
#         if self.logfile:
#             m = s.encode('ascii')
#             self.logfile.write('\n'.encode('ascii'))
#             self.logfile.write(m)
#             self.logfile.flush()
#         else:
#             m = "[{}] {}".format(self, s)
#             print(m)

#     def err(self, s):
#         self.log(s)
#         raise RuntimeError(s)

#     def apc_off(self, index):
#         while True:
#             try:
#                 apc = APC('apc1', 'apc', 'apc', quiet=True)
#             except pexpect.exceptions.EOF:
#                 self.log("APC Retry")
#                 continue
#             else:
#                 apc.off(index, 0)
#                 time.sleep(2)
#                 break

#     def apc_on(self, index):
#         while True:
#             try:
#                 apc = APC('apc1', 'apc', 'apc', quiet=True)
#             except:
#                 self.log("APC Retry")
#                 continue
#             else:
#                 apc.on(index)
#                 break

#     def init(self):
#         self.log("Initialising board at USB location [{}]".format(self.hub))
#         self._p = None

#         # If we find a disk at start of day, we must try to ensure it
#         # isn't mounted!
#         try:
#             part = self.usb.get_part(self.hub)
#         except usb.NoPartitions:
#             # We need to run through the full init now.
#             pass
#         else:
#             # We have a disk so let's not muck around too much.
#             self.log("WARN: Disk found {} at init, attempting unmount.".format(part))
#             cmd = 'sudo umount {device}'.format(device=part)
#             sp.run(cmd.split())

#         # We have to turn the boards off
#         self.off()

#         self.log("Power cycle the sdmux...")
#         self.apc_off(self.brd.sdmux.apc)
#         time.sleep(8)
#         self.apc_on(self.brd.sdmux.apc)

#         self.log("Rebinding whole HUB...")
#         self.usb.rebind(self.hub)

#         self._host()

#         self.log(str(self.p))

#         try:
#             part = self.usb.get_part(self.diskusb)
#         except usb.NoPartitions:
#             self.log("WARNING: Disk at {} has no partitions. May need to format disk".format(self.disk))

#         self.log("Disk [{disk}] DiskUsb [{diskusb}] Hub [{hub}] SDMUX [{sdmux}] SERIAL [{serial}]".format(
#             disk=self.disk,
#             diskusb=self.diskusb,
#             hub=self.hub,
#             sdmux=self.sdm,
#             serial=self.serial
#             ))

#     @property
#     def s(self):
#         if self._s is None:
#             self._s = serial.Serial(self.sdm, 9600)
#         return self._s

#     @property
#     def sdm(self):
#         return self.usb.get_sdmux(self.sdmux)

#     @property
#     def serial(self):
#         return self.usb.get_serial(self.hub)

#     @property
#     def p(self):
#         if self._p is None:
#             self.log("Configuring interact module...")
#             for _ in range(10):
#                 try:
#                     self._p = interact.serialSpawn(
#                         self.serial, board=self, logfile=self.blogfile)
#                 except RuntimeError as e:
#                     self.log("Failed to init serial [{}], rebooting board.", e)
#                     self.off()
#                     time.sleep(1)
#                     self.on()
#                     self._p = None
#                 else:
#                     # Wrappers around interact
#                     self.psr = self._p.psr
#                     self.send_newline = self._p.send_newline
#                     self.send = self._p.send
#                     self.waitr = self._p.waitr
#                     self.waitre = self._p.waitre
#                     self.snr = self._p.snr
#                     self.expect = self._p.expect
#                     self.echo_off = self._p.echo_off
#                     self.wait_for_quiet = self._p.wait_for_quiet
#                     return self._p

#             self.err('Could not connect to serial.')

#         return self._p

#     @property
#     def default_prompt(self):
#         return interact.default_prompt

#     def on(self):
#         self.log("Power ON")
#         return self.apc_on(self.apc)

#     def off(self):
#         self.log("Power OFF")
#         return self.apc_off(self.apc)

#     def sdm_host(self):
#         self.s.write(sdmux_map[self.sdmux_index]['host'])

#     def sdm_board(self):
#         self.s.write(sdmux_map[self.sdmux_index]['board'])

#     def test_disk(self):
#         # First we delay until we have permission
#         self.log("Test read access to [{}]".format(self.disk))
#         for _ in range(10):
#             try:
#                 with open(self.disk, "rb") as f:
#                     f.read(1)
#             except PermissionError:
#                 time.sleep(1)
#                 continue
#             except:
#                 self.log("Error with disk at [{}]".format(self.disk))
#                 raise
#             else:
#                 return

#     def host(self):
#         try:
#             self._host()
#         except:
#             self.log("Disk error! Trying to reinit!")
#         else:
#             return

#         try:
#             self.init()
#         except:
#             self.err("Fatal disk error")
#         else:
#             return

#     def _host(self):
#         self.log("Switching SD to host...")
#         ok = False

#         for _ in range(5):
#             self.sdm_host()

#             if self.diskusb:
#                 self.usb.rebind(self.diskusb)

#             # Sometimes, the disk fails to enumerate
#             self.log("Looking for disks...")
#             try:
#                 self.disk, self.diskusb = self.usb.get_block(self.hub)
#             except usb.NoDisks:
#                 self.log("No disks found yet, retrying...")
#                 continue

#             try:
#                 self.test_disk()
#             except:
#                 self.log("Disk error on testing, retry.")
#                 continue

#             self.log("DISKUSB at [{}]..".format(self.diskusb))
#             return

#         raise RuntimeError("Fatal disk error!")

#     def board(self):
#         self.log("Switching SD to board...")
#         self.usb.unbind(self.diskusb)
#         self.sdm_board()
#         time.sleep(1)

#     def unmount(self):
#         dev = self.usb.get_part(self.diskusb)
#         self.log("Umounting device {}...".format(dev))
#         cmd = 'sudo umount {device}'.format(device=dev)
#         return sp.run(cmd.split())

#     def mount(self):
#         uid = os.getuid()
#         dev = self.usb.get_part(self.diskusb)
#         self.log("Mounting device {} at {}....".format(dev, self.mount_path))
#         cmd = 'sudo mount -o uid={uid} {device} {path}'.format(
#             uid=uid, device=dev, path=self.mount_path)
#         return sp.run(cmd.split())

#     def root(self, path):
#         return "{}/{}".format(self.mount_path, path)
