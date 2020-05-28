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

## Find USB devices

___

<< Previous: [Tutorial: Adding a console controller](./2-1-tutorial-console.md) |
Next: [Tutorial: Adding a power controller](./2-3-tutorial-power.md) >>
