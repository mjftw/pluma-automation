# Tutorial: Hardware Control - Adding a Power Controller

One of the key features of the Automation Lab is the ability to turn devices on and off from within Python.

Depending on the hardware available to you the way this physically happens might be quite different, but the your code need not be.

There are many Power classes, each managing a different type of hardware. However they all inherit from the same base class `PowerBase`, meaning that they all have the same `on()`, `off()`, and `reboot()` methods.
The way you create an instance of a power class will differ depending on what it is, but the way you use it will not change.

For a full list of the supported power hardware, see [Supported Hardware](../supported-hardware.md).

## Power on and off

In this example we will be using the [IP Power 9258](https://www.aviosys.com/products/9858MT.html), a power distribution unit whose sockets can be switched on and off via HTTP requests.

```python
from farmcore import IPPowerPDU

power = IPPowerPDU(
    port=1
    host='192.168.0.30'
)


# Turn on socket 1 of the IP Power PDU at IP address 192.168.0.30
power.on()

# Turn it off
power.off()
```

## Rebooting

Rebooting a power device works in much the same way as turning it on and off, but with one additional parameter.

The parameter `reboot_delay` specifies how many seconds to wait between turning a device off, and switching it back on again.
It is important to be able to specify this as some devices won't turn off instantly. A device with a transformer in its power supply may remain powered on for a few seconds after the power is removed. This is due to the magnetic field in the coils collapsing, providing a final bit of power to the system.
If we were to turn the device back on one second after switching off the power, the device may not have actually turned off at all!

```python
from farmcore import IPPowerPDU

power = IPPowerPDU(
    port=1
    host='192.168.0.30',
    reboot_delay=3
)

# Turn off socket 1, wait 3 seconds, turn on socket 1
power.reboot()
```

___

<< Previous: [Tutorial: USB devices](./2-2-tutorial-usb.md) |
Next: [Tutorial: Adding a storage controller](./2-4-tutorial-storage.md) >>
