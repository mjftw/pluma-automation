# Tutorial: Hardware Control - Adding a Storage Controller

During testing it is often the case that a new firmware version must be loaded on the board. This can be done over the network using SSH, NFS, FTP etc in many cases, but this may not work when the device boots from the new firmware image.

To get around this issue, Pluma has support for the SD-Wire board from Tizen. This acts as an SD card multiplexer, able to switch the SD card between the the Pluma host and target board.  
Using this method the SD card could be attached to the Pluma host, a new boot image written to it, and passed back to the target before boot.

For more information on the SD-Wire, see [Supported Hardware](../supported-hardware.md).

## Mounting an SD Card to modify files

The SD card can be moved between the board and the Pluma host using the `to_board()` and `to_host()` methods of the `SDWire` class.

```python
from farmcore import SDWire
from farmutils import run_host_cmd

storage = SDWire()

# Turn off the board before removing boot media
power.off()

# Move SD card from target to host
storage.to_host()

device = hub.get_part('devnode')

# Use dd tool to write new firmware to the SD card
run_host_command(f'dd if="new_firmware.bin" of={device} bs=512')

# Run sync to ensure all data is written through from the cache to the SD card
run_host_command(f'sync')

# Swap the SD card back to the board
storage.to_board()

# Power on to boot the new firmware
power.on()
```

The above example assumes that the `power` and `hub` are defined elsewhere.
See previous tutorials on instructions for this.

___

<< Previous: [Tutorial: Adding a power controller](./2-3-tutorial-power.md) |
Next: [Tutorial: Bringing it all together](./2-5-tutorial-board.md) >>
