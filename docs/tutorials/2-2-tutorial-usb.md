# Tutorial: Hardware Control - USB Devices

The majority of the devices that the Automation Lab can control are USB based.
In this tutorial we'll view our USB tree, and look at how the Automation Lab discovers USB devices.

All of our interaction with the USB tree is done via the `Hub` class, which represents a USB Hub.
The words "USB Hub" probably make you think of an external USB splitter of sorts, but we can also use the `Hub` class without one, as you'll see later.

While the Automation Lab does have a `USB` class, this is just used for the low level system interaction and it's unlikely you'll need to look here.

## View USB tree

The easiest way to see what USB devices we have connected to our Lab host is to plot them.

```python
from farmcore import Hub

# Get a reference to USB Bus 1
usb_bus_1 = Hub('usb1')

# Display a plot of the USB tree
usb_bus_1.plot()
```

You should have a pop up window showing something like the image below.
![USB Bus 1 Plot](./usb_bus_1.svg)

You can see that on our test Lab host we have 2 hubs, 2 USB Relays, 1 USB -> UART adaptor, 1 USB -> Ethernet adapter, 1 unsupported "Unknown" device, and an SD-Wire containing an SD card with 2 partitions.
What you see will depend on your system configuration.

Any device that shows up with a name that isn't "Unknown Device" can be controlled with an Automation Lab class.

The above example uses X11 to display the plot, so this may not work on some systems.

You can also save the plot to an image:

```python
# Display a plot of the USB tree
usb_bus_1.plot(image_file='usb_bus_1', image_format='png')
```

You can use this to view the USB tree of a remote machine by starting SSH with the X-forwarding flag (`-Y`):

```shell
dev@labhost:~ $ ssh -Y pi@raspberrypi.local

pi@raspberry:~ $ ipython3
...
In [1]: from farmcore import Hub
In [2]: Hub('usb1').plot()
```

For a full list of available output formats see [Graphviz Output Formats](https://graphviz.org/doc/info/output.html).

## Understanding USB trees

The Linux kernel organises USB devices into a tree, found in sysfs at `/sys/bus/usb/devices`.

To see your USB tree you can use the `lsusb` tool:

```shell
pi@raspberry:~ $ lsusb --tree
/:  Bus 03.Port 1: Dev 1, Class=root_hub, Driver=dwc_otg/1p, 480M
/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/4p, 5000M
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/1p, 480M
    |__ Port 1: Dev 2, If 0, Class=Hub, Driver=hub/4p, 480M
        |__ Port 1: Dev 3, If 0, Class=Hub, Driver=hub/4p, 480M
            |__ Port 1: Dev 5, If 0, Class=Vendor Specific Class, Driver=ftdi_sio, 12M
            |__ Port 2: Dev 12, If 0, Class=Vendor Specific Class, Driver=ftdi_sio, 480M
            |__ Port 3: Dev 7, If 0, Class=Hub, Driver=hub/3p, 480M
                |__ Port 1: Dev 9, If 0, Class=Mass Storage, Driver=usb-storage, 480M
                |__ Port 2: Dev 10, If 0, Class=Vendor Specific Class, Driver=, 12M
            |__ Port 4: Dev 8, If 0, Class=Vendor Specific Class, Driver=asix, 480M
        |__ Port 2: Dev 4, If 0, Class=Vendor Specific Class, Driver=ftdi_sio, 12M
```

The `tree` tool can also be used.

E.g. to view the tree for the USB 1 bus:

```shell
pi@raspberry:~ $ tree /sys/bus/usb/devices/usb1/ -d --matchdirs -P '*1-'

/sys/bus/usb/devices/usb1/
├── 1-0:1.0
│   └── usb1-port1
├── 1-1
│   ├── 1-1.1
│   │   ├── 1-1.1.1
│   │   │   ├── 1-1.1.1:1.0
│   │   │   │   └── ttyUSB1
│   │   ├── 1-1.1:1.0
│   │   │   ├── 1-1.1-port1
│   │   │   ├── 1-1.1-port2
│   │   │   ├── 1-1.1-port3
│   │   │   ├── 1-1.1-port4
│   │   ├── 1-1.1.2
│   │   │   ├── 1-1.1.2:1.0
│   │   │   │   └── ttyUSB2
│   │   ├── 1-1.1.3
│   │   │   ├── 1-1.1.3.1
│   │   │   │   ├── 1-1.1.3.1:1.0
│   │   │   │   │   ├── host0
│   │   │   │   │   │   └── target0:0:0
│   │   │   │   │   │       ├── 0:0:0:0
│   │   │   │   │   │       │   ├── block
│   │   │   │   │   │       │   │   └── sda
│   │   │   │   │   │       │   │       ├── sda1
│   │   │   │   │   │       │   │       ├── sda2
│   │   │   ├── 1-1.1.3:1.0
│   │   │   │   ├── 1-1.1.3-port1
│   │   │   │   ├── 1-1.1.3-port2
│   │   │   │   ├── 1-1.1.3-port3
│   │   │   ├── 1-1.1.3.2
│   │   │   ├── 1-1.1.3.2
│   │   │   │   ├── 1-1.1.3.2:1.0
│   │   ├── 1-1.1.4
│   │   │   ├── 1-1.1.4:1.0
│   │   │   │   ├── net
│   │   │   │   │   └── eth1
│   ├── 1-1:1.0
│   │   ├── 1-1-port1
│   │   ├── 1-1-port2
│   │   ├── 1-1-port3
│   │   ├── 1-1-port4
│   ├── 1-1.2
│   │   ├── 1-1.2:1.0
│   │   │   └── ttyUSB0
...

183 directories
```

The output shown above is cut down to emphasise the important details from what you'll actually see when you run that command.

The Linux kernel gives each USB device an address, defined by what USB bus and hubs it is connected to.

The generic address form is: `X-Y.Z:A.B`

Each field identifies where your device is connected within the USB tree.

- `X` is the number of the USB bus on the system
- `Y` is port number in use on that bus
- `Z` is optional and specifies the port number of a connected USB hub.
  - If a USB hub is connected to a port on another USB hub then a new number is added.
- `A` is the interface number (we're not interested in this)
- `B` is the configuration number  (we're not interested in this)

E.g.

`1-2` means port 2 on USB bus 1
`1-2.3` means port 3 of a USB hub connected to port 2 of USB bus 1
`1-2.3.4` means port 4 of a USB hub connected to port 3 of a USB hub connected to port 2 of USB bus 1

With this pattern in mind, look again at the plot of the USB tree in the previous section.
Looking at the device `Serial0` you'll see that it's USB address is `1-1.1.2`.
In other words, it's connected to port 2 of a USB hub connected to port 1 of a USB hub connected to port 1 of USB bus 1.

In the plot you'll also see that `Block0`, `Partition0`, and `Partition1` all share the same USB address (`1-1.1.3.1`).
This is because they are all the same device on the USB bus, but with different interface and configuration numbers, although these are not shown in the diagram.

## How to find a device's USB address

The easiest way is probably to watch the Linux kernel log while plugging the device in.

```shell
pi@raspberry:~ $ dmesg -w
** Plugged in USB relay***

[1388395.063692] usb 1-1.2: new full-speed USB device number 13 using xhci_hcd
[1388395.209362] usb 1-1.2: New USB device found, idVendor=0403, idProduct=6001, bcdDevice= 6.00
[1388395.209378] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[1388395.209390] usb 1-1.2: Product: DLP-IOR4
[1388395.209403] usb 1-1.2: Manufacturer: DLP Design
[1388395.209414] usb 1-1.2: SerialNumber: 12345678
[1388395.236533] ftdi_sio 1-1.2:1.0: FTDI USB Serial Device converter detected
[1388395.236671] usb 1-1.2: Detected FT232RL
[1388395.241840] usb 1-1.2: FTDI USB Serial Device converter now attached to ttyUSB0
```

From this you can see that the USB relay has the USB address `1-1.2`.

You could also use `lsusb` as above, although you'll have to work out the actual address yourself.

As we've already seen, the `farmcore` class `Hub` can also give you this information as a plot.
We can also get the Hub class to find us the USB address (and other information) of a given type of USB device, as we'll see in the next section.

## Find USB devices

___

<< Previous: [Tutorial: Adding a console controller](./2-1-tutorial-console.md) |
Next: [Tutorial: Adding a power controller](./2-3-tutorial-power.md) >>
