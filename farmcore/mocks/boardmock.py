import time

from ..board import Board
from ..baseclasses import PowerBase
from .serialconsolemock import SerialConsoleMock


class BoardMock(Board):
    class BoardMockPower(PowerBase):
        def __init__(self, board):
            self.board = board
            PowerBase.__init__(self)

        @PowerBase.on
        def on(self):
            self.board.console.open()

        @PowerBase.off
        def off(self):
            self.board.console.close()

    def __init__(self):
        Board.__init__(
            self,
            name='Mock Board',
            console=SerialConsoleMock(
                child_function=_console_child_function
            ),
            power=self.BoardMockPower(
                board=self
            )
        )


def _console_child_function(*args):
    boot_text = '''
[    0.000000] Booting Linux on physical CPU 0x0
[    0.000000] Linux version 4.14.98-v7+ (dom@dom-XPS-13-9370) (gcc version 4.9.3 (crosstool-NG crosstool-ng-1.22.0-88-g8460611)) #1200 SMP Tue Feb 12 20:27:48 GMT 2019
[    0.000000] CPU: ARMv7 Processor [410fd034] revision 4 (ARMv7), cr=10c5383d
[    0.000000] CPU: div instructions available: patching division code
[    0.000000] CPU: PIPT / VIPT nonaliasing data cache, VIPT aliasing instruction cache
[    0.000000] OF: fdt: Machine model: Raspberry Pi 3 Model B Plus Rev 1.3
[    0.000000] Memory policy: Data cache writealloc
[    0.000000] cma: Reserved 8 MiB at 0x37800000
[    0.000000] On node 0 totalpages: 229376
[    0.000000] free_area_init_node: node 0, pgdat 80c85780, node_mem_map b7014000
[    0.000000]   Normal zone: 2016 pages used for memmap
[    0.000000]   Normal zone: 0 pages reserved
[    0.000000]   Normal zone: 229376 pages, LIFO batch:31
[    0.000000] percpu: Embedded 17 pages/cpu @b6fbd000 s38720 r8192 d22720 u69632
[    0.000000] pcpu-alloc: s38720 r8192 d22720 u69632 alloc=17*4096
[    0.000000] pcpu-alloc: [0] 0 [0] 1 [0] 2 [0] 3 
[    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 227360
[    0.000000] Kernel command line: 8250.nr_uarts=0 bcm2708_fb.fbwidth=1920 bcm2708_fb.fbheight=1080 bcm2708_fb.fbswap=1 vc_mem.mem_base=0x3ec00000 vc_mem.mem_size=0x40000000  dwc_otg.lpm_enable=0 console=ttyS0,115200 console=tty1 root=PARTUUID=ff0385b4-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles
[    0.000000] PID hash table entries: 4096 (order: 2, 16384 bytes)
[    0.000000] Dentry cache hash table entries: 131072 (order: 7, 524288 bytes)
[    0.000000] Inode-cache hash table entries: 65536 (order: 6, 262144 bytes)
[    0.000000] Memory: 887452K/917504K available (7168K kernel code, 577K rwdata, 2080K rodata, 1024K init, 698K bss, 21860K reserved, 8192K cma-reserved)
[    0.000000] Virtual kernel memory layout:
                vector  : 0xffff0000 - 0xffff1000   (   4 kB)
                fixmap  : 0xffc00000 - 0xfff00000   (3072 kB)
                vmalloc : 0xb8800000 - 0xff800000   (1136 MB)
                lowmem  : 0x80000000 - 0xb8000000   ( 896 MB)
                modules : 0x7f000000 - 0x80000000   (  16 MB)
                    .text : 0x80008000 - 0x80800000   (8160 kB)
                    .init : 0x80b00000 - 0x80c00000   (1024 kB)
                    .data : 0x80c00000 - 0x80c906d4   ( 578 kB)
                    .bss : 0x80c97ef8 - 0x80d468f0   ( 699 kB)
[    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=4, Nodes=1
[    0.000000] ftrace: allocating 25298 entries in 75 pages
[    0.000000] Hierarchical RCU implementation.
[    0.000000] NR_IRQS: 16, nr_irqs: 16, preallocated irqs: 16
[    0.000000] arch_timer: cp15 timer(s) running at 19.20MHz (phys).
[    0.000000] clocksource: arch_sys_counter: mask: 0xffffffffffffff max_cycles: 0x46d987e47, max_idle_ns: 440795202767 ns
[    0.000006] sched_clock: 56 bits at 19MHz, resolution 52ns, wraps every 4398046511078ns
[    0.000018] Switching to timer-based delay loop, resolution 52ns
[    0.000266] Console: colour dummy device 80x30
[    0.000285] console [tty1] enabled
[    0.000310] Calibrating delay loop (skipped), value calculated using timer frequency.. 38.40 BogoMIPS (lpj=192000)
[    0.000325] pid_max: default: 32768 minimum: 301
[    0.000645] Mount-cache hash table entries: 2048 (order: 1, 8192 bytes)
[    0.000660] Mountpoint-cache hash table entries: 2048 (order: 1, 8192 bytes)
[    0.001602] Disabling memory control group subsystem
[    0.001675] CPU: Testing write buffer coherency: ok
[    0.002091] CPU0: thread -1, cpu 0, socket 0, mpidr 80000000
[    0.002494] Setting up static identity map for 0x100000 - 0x10003c
[    0.002615] Hierarchical SRCU implementation.
[    0.003291] smp: Bringing up secondary CPUs ...
[    0.004073] CPU1: thread -1, cpu 1, socket 0, mpidr 80000001
[    0.004918] CPU2: thread -1, cpu 2, socket 0, mpidr 80000002
[    0.005745] CPU3: thread -1, cpu 3, socket 0, mpidr 80000003
[    0.005849] smp: Brought up 1 node, 4 CPUs
[    0.005860] SMP: Total of 4 processors activated (153.60 BogoMIPS).
[    0.005865] CPU: All CPU(s) started in HYP mode.
[    0.005869] CPU: Virtualization extensions available.
[    0.006778] devtmpfs: initialized
[    0.017279] random: get_random_u32 called from bucket_table_alloc+0xfc/0x24c with crng_init=0
[    0.018051] VFP support v0.3: implementor 41 architecture 3 part 40 variant 3 rev 4
[    0.018273] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 19112604462750000 ns
[    0.018290] futex hash table entries: 1024 (order: 4, 65536 bytes)
[    0.018845] pinctrl core: initialized pinctrl subsystem
[    0.019603] NET: Registered protocol family 16
[    0.022362] DMA: preallocated 1024 KiB pool for atomic coherent allocations
[    0.027361] hw-breakpoint: found 5 (+1 reserved) breakpoint and 4 watchpoint registers.
[    0.027368] hw-breakpoint: maximum watchpoint size is 8 bytes.
[    0.027573] Serial: AMBA PL011 UART driver
[    0.029232] bcm2835-mbox 3f00b880.mailbox: mailbox enabled
[    0.029693] uart-pl011 3f201000.serial: could not find pctldev for node /soc/gpio@7e200000/uart0_pins, deferring probe
[    0.061647] bcm2835-dma 3f007000.dma: DMA legacy API manager at b8813000, dmachans=0x1
[    0.063106] SCSI subsystem initialized
[    0.063326] usbcore: registered new interface driver usbfs
[    0.063378] usbcore: registered new interface driver hub
[    0.063467] usbcore: registered new device driver usb
[    0.070086] raspberrypi-firmware soc:firmware: Attached to firmware from 2019-03-27 15:48
[    0.071529] clocksource: Switched to clocksource arch_sys_counter
[    0.148295] VFS: Disk quotas dquot_6.6.0
[    0.148378] VFS: Dquot-cache hash table entries: 1024 (order 0, 4096 bytes)
[    0.148562] FS-Cache: Loaded
[    0.148744] CacheFiles: Loaded
[    0.156789] NET: Registered protocol family 2
[    0.157507] TCP established hash table entries: 8192 (order: 3, 32768 bytes)
[    0.157617] TCP bind hash table entries: 8192 (order: 4, 65536 bytes)
[    0.157802] TCP: Hash tables configured (established 8192 bind 8192)
[    0.157930] UDP hash table entries: 512 (order: 2, 16384 bytes)
[    0.157974] UDP-Lite hash table entries: 512 (order: 2, 16384 bytes)
[    0.158201] NET: Registered protocol family 1
[    0.158674] RPC: Registered named UNIX socket transport module.
[    0.158679] RPC: Registered udp transport module.
[    0.158684] RPC: Registered tcp transport module.
[    0.158690] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.160351] hw perfevents: enabled with armv7_cortex_a7 PMU driver, 7 counters available
[    0.163127] workingset: timestamp_bits=14 max_order=18 bucket_order=4
[    0.171290] FS-Cache: Netfs 'nfs' registered for caching
[    0.171931] NFS: Registering the id_resolver key type
[    0.171961] Key type id_resolver registered
[    0.171966] Key type id_legacy registered
[    0.171982] nfs4filelayout_init: NFSv4 File Layout Driver Registering...
[    0.173926] Block layer SCSI generic (bsg) driver version 0.4 loaded (major 251)
[    0.174055] io scheduler noop registered
[    0.174062] io scheduler deadline registered (default)
[    0.174233] io scheduler cfq registered
[    0.174239] io scheduler mq-deadline registered
[    0.174245] io scheduler kyber registered
[    0.176576] BCM2708FB: allocated DMA memory f7900000
[    0.176603] BCM2708FB: allocated DMA channel 0 @ b8813000
[    0.234162] Console: switching to colour frame buffer device 240x67
[    0.269186] bcm2835-rng 3f104000.rng: hwrng registered
[    0.269318] vc-mem: phys_addr:0x00000000 mem_base=0x3ec00000 mem_size:0x40000000(1024 MiB)
[    0.269765] vc-sm: Videocore shared memory driver
[    0.270039] gpiomem-bcm2835 3f200000.gpiomem: Initialised: Registers at 0x3f200000
[    0.279901] brd: module loaded
[    0.288995] loop: module loaded
[    0.289011] Loading iSCSI transport class v2.0-870.
[    0.289740] libphy: Fixed MDIO Bus: probed
[    0.289844] usbcore: registered new interface driver lan78xx
[    0.289907] usbcore: registered new interface driver smsc95xx
[    0.289923] dwc_otg: version 3.00a 10-AUG-2012 (platform bus)
[    0.317840] dwc_otg 3f980000.usb: base=0xf0980000
[    0.518062] Core Release: 2.80a
[    0.518073] Setting default values for core params
[    0.518106] Finished setting default values for core params
[    0.718373] Using Buffer DMA mode
[    0.718380] Periodic Transfer Interrupt Enhancement - disabled
[    0.718386] Multiprocessor Interrupt Enhancement - disabled
[    0.718392] OTG VER PARAM: 0, OTG VER FLAG: 0
[    0.718406] Dedicated Tx FIFOs mode
[    0.718739] WARN::dwc_otg_hcd_init:1046: FIQ DMA bounce buffers: virt = 0xb7914000 dma = 0xf7914000 len=9024
[    0.718765] FIQ FSM acceleration enabled for :
            Non-periodic Split Transactions
            Periodic Split Transactions
            High-Speed Isochronous Endpoints
            Interrupt/Control Split Transaction hack enabled
[    0.718772] dwc_otg: Microframe scheduler enabled
[    0.718827] WARN::hcd_init_fiq:459: FIQ on core 1 at 0x805ed94c
[    0.718838] WARN::hcd_init_fiq:460: FIQ ASM at 0x805edcb4 length 36
[    0.718852] WARN::hcd_init_fiq:486: MPHI regs_base at 0xf0006000
[    0.718907] dwc_otg 3f980000.usb: DWC OTG Controller
[    0.718939] dwc_otg 3f980000.usb: new USB bus registered, assigned bus number 1
[    0.718970] dwc_otg 3f980000.usb: irq 62, io mem 0x00000000
[    0.719020] Init: Port Power? op_state=1
[    0.719025] Init: Power Port (0)
[    0.719246] usb usb1: New USB device found, idVendor=1d6b, idProduct=0002
[    0.719258] usb usb1: New USB device strings: Mfr=3, Product=2, SerialNumber=1
[    0.719267] usb usb1: Product: DWC OTG Controller
[    0.719275] usb usb1: Manufacturer: Linux 4.14.98-v7+ dwc_otg_hcd
[    0.719283] usb usb1: SerialNumber: 3f980000.usb
[    0.719902] hub 1-0:1.0: USB hub found
[    0.719942] hub 1-0:1.0: 1 port detected
[    0.720492] dwc_otg: FIQ enabled
[    0.720497] dwc_otg: NAK holdoff enabled
[    0.720503] dwc_otg: FIQ split-transaction FSM enabled
[    0.720512] Module dwc_common_port init
[    0.720777] usbcore: registered new interface driver usb-storage
[    0.720950] mousedev: PS/2 mouse device common for all mice
[    0.721025] IR NEC protocol handler initialized
[    0.721031] IR RC5(x/sz) protocol handler initialized
[    0.721037] IR RC6 protocol handler initialized
[    0.721042] IR JVC protocol handler initialized
[    0.721047] IR Sony protocol handler initialized
[    0.721052] IR SANYO protocol handler initialized
[    0.721057] IR Sharp protocol handler initialized
[    0.721062] IR MCE Keyboard/mouse protocol handler initialized
[    0.721067] IR XMP protocol handler initialized
[    0.721816] bcm2835-wdt 3f100000.watchdog: Broadcom BCM2835 watchdog timer
[    0.722101] bcm2835-cpufreq: min=600000 max=1400000
[    0.722468] sdhci: Secure Digital Host Controller Interface driver
[    0.722473] sdhci: Copyright(c) Pierre Ossman
[    0.722836] mmc-bcm2835 3f300000.mmc: could not get clk, deferring probe
[    0.723163] sdhost-bcm2835 3f202000.mmc: could not get clk, deferring probe
[    0.723259] sdhci-pltfm: SDHCI platform and OF driver helper
[    0.724713] ledtrig-cpu: registered to indicate activity on CPUs
[    0.724874] hidraw: raw HID events driver (C) Jiri Kosina
[    0.725030] usbcore: registered new interface driver usbhid
[    0.725035] usbhid: USB HID core driver
[    0.725653] vchiq: vchiq_init_state: slot_zero = b7980000, is_master = 0
[    0.727232] [vc_sm_connected_init]: start
[    0.736901] [vc_sm_connected_init]: end - returning 0
[    0.737544] Initializing XFRM netlink socket
[    0.737567] NET: Registered protocol family 17
[    0.737668] Key type dns_resolver registered
[    0.738216] Registering SWP/SWPB emulation handler
[    0.738818] registered taskstats version 1
[    0.744870] uart-pl011 3f201000.serial: cts_event_workaround enabled
[    0.744953] 3f201000.serial: ttyAMA0 at MMIO 0x3f201000 (irq = 87, base_baud = 0) is a PL011 rev2
[    0.746864] mmc-bcm2835 3f300000.mmc: mmc_debug:0 mmc_debug2:0
[    0.746874] mmc-bcm2835 3f300000.mmc: DMA channel allocated
[    0.812165] sdhost: log_buf @ b7913000 (f7913000)
[    0.849006] mmc1: queuing unknown CIS tuple 0x80 (2 bytes)
[    0.850578] mmc1: queuing unknown CIS tuple 0x80 (3 bytes)
[    0.852143] mmc1: queuing unknown CIS tuple 0x80 (3 bytes)
[    0.854918] mmc1: queuing unknown CIS tuple 0x80 (7 bytes)
[    0.891550] mmc0: sdhost-bcm2835 loaded - DMA enabled (>1)
[    0.892632] of_cfs_init
[    0.892787] of_cfs_init: OK
[    0.893336] Waiting for root device PARTUUID=ff0385b4-02...
[    0.931791] random: fast init done
[    0.938892] mmc1: new high speed SDIO card at address 0001
[    0.941632] Indeed it is in host mode hprt0 = 00021501
[    1.008878] mmc0: host does not support reading read-only switch, assuming write-enable
[    1.011829] mmc0: new high speed SDHC card at address b368
[    1.012350] mmcblk0: mmc0:b368 USD   3.76 GiB
[    1.013961]  mmcblk0: p1 p2
[    1.044193] EXT4-fs (mmcblk0p2): INFO: recovery required on readonly filesystem
[    1.044200] EXT4-fs (mmcblk0p2): write access will be enabled during recovery
[    1.151599] usb 1-1: new high-speed USB device number 2 using dwc_otg
[    1.151736] Indeed it is in host mode hprt0 = 00001101
[    1.391810] usb 1-1: New USB device found, idVendor=0424, idProduct=2514
[    1.391821] usb 1-1: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    1.392514] hub 1-1:1.0: USB hub found
[    1.392605] hub 1-1:1.0: 4 ports detected
[    1.711556] usb 1-1.1: new high-speed USB device number 3 using dwc_otg
[    1.841764] usb 1-1.1: New USB device found, idVendor=0424, idProduct=2514
[    1.841776] usb 1-1.1: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    1.842266] hub 1-1.1:1.0: USB hub found
[    1.842350] hub 1-1.1:1.0: 3 ports detected
[    2.195126] dwc_otg_handle_wakeup_detected_intr lxstate = 2
[    2.571554] usb 1-1.1.1: new high-speed USB device number 4 using dwc_otg
[    2.701930] usb 1-1.1.1: New USB device found, idVendor=0424, idProduct=7800
[    2.701941] usb 1-1.1.1: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    2.967059] libphy: lan78xx-mdiobus: probed
[    2.971836] lan78xx 1-1.1.1:1.0 (unnamed net_device) (uninitialized): int urb period 64
[    4.732630] EXT4-fs (mmcblk0p2): recovery complete
[    5.425858] EXT4-fs (mmcblk0p2): mounted filesystem with ordered data mode. Opts: (null)
[    5.425915] VFS: Mounted root (ext4 filesystem) readonly on device 179:2.
[    5.426796] devtmpfs: mounted
[    5.430142] Freeing unused kernel memory: 1024K
[    5.916691] systemd[1]: System time before build time, advancing clock.
[    6.050774] NET: Registered protocol family 10
[    6.052099] Segment Routing with IPv6
[    6.079269] ip_tables: (C) 2000-2006 Netfilter Core Team
[    6.100690] random: systemd: uninitialized urandom read (16 bytes read)
[    6.106638] systemd[1]: systemd 232 running in system mode. (+PAM +AUDIT +SELINUX +IMA +APPARMOR +SMACK +SYSVINIT +UTMP +LIBCRYPTSETUP +GCRYPT +GNUTLS +ACL +XZ +LZ4 +SECCOMP +BLKID +ELFUTILS +KMOD +IDN)
[    6.107207] systemd[1]: Detected architecture arm.
[    6.108150] systemd[1]: Set hostname to <raspberrypi>.
[    6.151494] random: systemd: uninitialized urandom read (16 bytes read)
[    6.187948] random: systemd-gpt-aut: uninitialized urandom read (16 bytes read)
[    6.743708] systemd[1]: Listening on Syslog Socket.
[    6.744806] systemd[1]: Created slice System Slice.
[    6.745143] systemd[1]: Listening on Journal Socket.
[    6.748544] systemd[1]: Starting Create list of required static device nodes for the current kernel...
[    6.749732] systemd[1]: Created slice system-getty.slice.
[    6.750169] systemd[1]: Listening on udev Control Socket.
[    6.750478] systemd[1]: Listening on /dev/initctl Compatibility Named Pipe.
[    6.863248] i2c /dev entries driver
[    7.304079] EXT4-fs (mmcblk0p2): re-mounted. Opts: (null)
[    7.399895] systemd-journald[96]: Received request to flush runtime journal from PID 1
[    7.921882] snd_bcm2835: module is from the staging directory, the quality is unknown, you have been warned.
[    7.925491] bcm2835_alsa bcm2835_alsa: card created with 8 channels
[    8.080131] brcmfmac: F1 signature read @0x18000000=0x15264345
[    8.088564] brcmfmac: brcmf_fw_map_chip_to_name: using brcm/brcmfmac43455-sdio.bin for chip 0x004345(17221) rev 0x000006
[    8.089284] usbcore: registered new interface driver brcmfmac
[    8.372384] random: crng init done
[    8.372400] random: 7 urandom warning(s) missed due to ratelimiting
[    8.445736] brcmfmac: brcmf_c_preinit_dcmds: Firmware version = wl0: Feb 27 2018 03:15:32 version 7.45.154 (r684107 CY) FWID 01-4fbe0b04
[    8.446313] brcmfmac: brcmf_c_preinit_dcmds: CLM version = API: 12.2 Data: 9.10.105 Compiler: 1.29.4 ClmImport: 1.36.3 Creation: 2018-03-09 18:56:28 
[    9.582286] uart-pl011 3f201000.serial: no DMA platform data
[    9.674325] IPv6: ADDRCONF(NETDEV_UP): wlan0: link is not ready
[    9.674344] brcmfmac: power management disabled
[    9.942860] IPv6: ADDRCONF(NETDEV_UP): eth0: link is not ready
[    9.967353] IPv6: ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[   10.753392] Adding 102396k swap on /var/swap.  Priority:-2 extents:1 across:102396k SSFS
[   16.209129] Bluetooth: Core ver 2.22
[   16.209192] NET: Registered protocol family 31
[   16.209195] Bluetooth: HCI device and connection manager initialized
[   16.209218] Bluetooth: HCI socket layer initialized
[   16.209225] Bluetooth: L2CAP socket layer initialized
[   16.209249] Bluetooth: SCO socket layer initialized
[   16.220473] Bluetooth: HCI UART driver ver 2.3
[   16.220481] Bluetooth: HCI UART protocol H4 registered
[   16.220484] Bluetooth: HCI UART protocol Three-wire (H5) registered
[   16.220611] Bluetooth: HCI UART protocol Broadcom registered
[   16.883862] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
[   16.883874] Bluetooth: BNEP filters: protocol multicast
[   16.883890] Bluetooth: BNEP socket layer initialized
[   16.950429] Bluetooth: RFCOMM TTY layer initialized
[   16.950462] Bluetooth: RFCOMM socket layer initialized
[   16.950498] Bluetooth: RFCOMM ver 1.11
[   28.952144] fuse init (API version 7.26)
    '''.split('\n')

    for line in boot_text:
        print(line)
        time.sleep(0.02)

    user = None
    while user != 'root':
        time.sleep(2)
        user = input('Mock Board login:')

    print('Mock board finished booting')
    print('Going into echo mode')

    while True:
        recieved = input()
        print(recieved)
