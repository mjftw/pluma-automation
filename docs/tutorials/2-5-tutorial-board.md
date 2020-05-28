# Tutorial: Hardware Control - Bringing it all together

The Board class is the software representation of our DUT, and our main entry point for hardware control.  
It mostly acts as a common container for the other hardware control classes. E.g. Console, Power, Storage.

Create a board instance:

```python
from farmcore import Board

board = Board(name='DUT')
```

While we have created a board, it can't do much without being given some hardware controllers.

## Login

## Reboot and validate

___

<< Previous: [Tutorial: Adding a storage controller](./2-4-tutorial-storage.md) |
Next: [Tutorial: Test Framework](./3-tutorial-test-framework.md) >>
