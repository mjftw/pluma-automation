# Tutorial: Hardware Control

## Using the Board class

The Board class is the software representation of our DUT, and our main entry point for hardware control.  
It mostly acts as a common container for the other hardware control classes. E.g. Console, Power, Storage.

Create a board instance:

```python
from farmcore import Board

board = Board(name='DUT')
```

While we have created a board, it can't do much without being given some hardware controllers.

## Using the Hub class

### Understanding USB trees

### Find usb devices

### View usb tree

## Adding a power controller

### Rebooting a board

## Adding a storage controller

### Mounting an SD Card to modify files

### Viewing modified files on the board

## Advanced Board control

### Login

### Reboot and validate

___

<< Previous: [Tutorial: Introduction](./1-tutorial-introduction.md) |
Next: [Tutorial: Adding a console controller](./2-1-tutorial-console.md) >>
