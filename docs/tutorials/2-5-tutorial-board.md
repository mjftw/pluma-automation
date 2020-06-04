# Tutorial: Hardware Control - Bringing it All Together

The Board class is the software representation of our board, acting as a top level reference for the hardware control classes (`console`, `power`, etc).

The following example assumes that `my_hub`, `my_power`, `my_storage`, and `my_console` have already been defined elsewhere. These can be any variant of the hardware control classes (e.g. `HostConsole`, `SerialConsole`, or something else for `console`).

```python
from farmcore import Board

# Defined elsewhere for this example
from my_hardware import my_hub, my_power, my_storage, my_console

rpi4_board = Board(
    name='rpi4',
    hub=my_hub,
    power=my_power,
    storage=my_storage,
    console=my_console
)
```

All of the hardware control class parameters are optional, although the `Board` instance won't do much without them.

The hardware controllers are then always accessed through the `board` instance, rather than directly.

For example:

```python
# Defined elsewhere for this example
from my_boards import rpi4_board as board

# Reboot the board
board.power.reboot()

# Send "ls" command to board
board.console.send('ls')

# Find USB relay attached to board's dedicated hub
board.hub.get_relay()

# Move board's SD card to host ready to transfer files or images
board.storage.to_host()
```

You'll notice that once the board class is defined, we no longer need to know what any of the hardware control classes are. We access them in the same way, with the same methods, regardless of the underlying control class.

This is very important when using the test framework as the `TestRunner` uses this top level board to access the hardware, with no knowledge of what the specific hardware is. This is covered in more detail in the upcoming [Tutorial: Test Framework](./3-tutorial-test-framework.md).

## Reboot and validate

As well as acting as a top level hardware reference, the `Board` class leverages the functionality of the contained hardware controllers to provide some helper methods.
The `reboot_and_validate()` method will first call the `Board`'s `power` instances `reboot()` method, then watch the `Board`'s `console` for a known boot string.

```python
from farmcore import BoardBootValidationError

# Board defined elsewhere for this example
from my_hardware import my_board as board

# Reboot, then watch for "login:" on the console
try
    board.reboot_and_validate()
except BoardBootValidationError:
    board.log('Oh no! Boot failed!')
    raise

board.log('Boot success!')

```

## Login

Another helper provided by the `Board` is the `login()` method. This method uses additional configuration provided to the `Board` on creation to perform an automated login using the `Board`'s `console`.  
The login is actually performed using the `console`'s `login()` method.

```python
from farmcore import Board, ConsoleLoginFailedError

# Control classes defined elsewhere for this example
from my_hardware import console, power


board = Board(
    name='rpi4',
    login_user='pi',
    login_pass='raspberry', # Omit if user has no password
    console=console,
    power=power
)

# We reboot our board to a known working state so we know that it is ready for login
# You could skip this step if you are sure the board is already at the login prompt
board.reboot_and_validate()

try:
    board.login()
# We can catch the exception raised if login fails
except ConsoleLoginFailedError:
    board.log('Oh no, login failed!')
    raise

board.log('Login success!')
```

The above example assumes that we are trying to log into a Unix style [getty](https://en.wikipedia.org/wiki/Getty_(Unix)), and watches the console for the message "login:" to know when to start the login.
It also expects the password prompt to be "Password:", and will not enter the password until it sees this.

If these defaults do not work for your system, they can be changed with the board parameters `login_user_match` and `login_pass_match`.

```python
from farmcore import Board

# Control classes defined elsewhere for this example
from my_hardware import console


board = Board(
    name='my_unusual_board',
    console=console,
    login_user_match='Enter username:',
    login_user='dave',
    login_pass_match='Enter password:',
    login_pass='bad_password'
)
```

If after the password is sent to the console, the `login_pass_match` is received again, it is assumed that the password was incorrect and the login has failed.
If this is not the case then the login is assumed to have succeeded, as this is the default behaviour of the Linux login prompt.  
If you know in advance what the terminal prompt is for the board, then you can provide this to the `Board` so it knows for sure the login was a success.
In other words, if we see the `prompt` after we entered the password then the login has succeeded. If not, it has failed.  
This method can be more robust, but requires additional knowledge of the board's console behaviour in advance.


```python
from farmcore import Board

# Control classes defined elsewhere for this example
from my_hardware import console


board = Board(
    name='my_unusual_board',
    console=console,
    login_user='pi',
    login_pass='raspberry',
    prompt='pi@raspberrypi:~ $'
)
```

Often before calling the `login()` method we call the `reboot_and_validate()` method to ensure the board is booted and ready for login.
If we have defined the `Board`'s `prompt`, and during the `reboot_and_validate()` process the `prompt` was received rather than the boot string, then we know that there is no need to attempt to login.
The board is already passed the point where we'd need to login, and if we tried to login it would fail!  
To get around this issue, if `login()` is called after `reboot_and_validate()` received the `prompt` then the login is not attempted.
To know whether this is not the case you can read the board's `booted_to_prompt` property

```python
from farmcore import Board, ConsoleLoginFailedError

# Control classes defined elsewhere for this example
from my_hardware import console, power


board = Board(
    name='rpi4',
    console=console,
    login_user='pi',
    login_pass='raspberry',
    prompt='pi@raspberrypi:~ $'
)


board.reboot_and_validate()

print(board.booted_to_prompt)
# True

# Will succeed without checking the console since we know the board has
# already booted to the terminal prompt
board.login()
```

## Logging

___

<< Previous: [Tutorial: Adding a storage controller](./2-4-tutorial-storage.md) |
Next: [Tutorial: Test Framework](./3-tutorial-test-framework.md) >>
