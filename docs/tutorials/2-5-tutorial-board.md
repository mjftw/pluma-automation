# Tutorial: Hardware Control - Bringing it All Together

The Board class is the software representation of our board, acting as a top level reference for the hardware control classes (`console`, `power`, etc).

The following example assumes that `my_hub`, `my_power`, `my_storage`, and `my_console` have already been defined elsewhere. These can be any variant of the hardware control classes (e.g. `HostConsole`, `SerialConsole`, or something else for `console`).

```python
from pluma import Board

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
from pluma import BoardBootValidationError

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

By default this boot string will be set to `login:`, but you can override this for your system when creating the `Board` instance.  
To pick a reasonable value you should watch the console log during boot, and find a word or phrase that you are sure only occurs once the board has finished booting.
For the example below we have chosen `Poky` as our `bootstr`. This would be a reasonable choice if booting a [Yocto](https://www.yoctoproject.org/) based Linux distribution.

```python
from pluma import Board

imx6_board = Board(
    name='imx6_yocto',
    bootstr='Poky'
)
```

## Login

Another helper provided by the `Board` is the `login()` method. This method uses additional configuration provided to the `Board` on creation to perform an automated login using the `Board`'s `console`.  
The login is actually performed using the `console`'s `login()` method.

```python
from pluma import Board, ConsoleLoginFailedError, SystemContext, Credentials

# Control classes defined elsewhere for this example
from my_hardware import console, power


board = Board(
    name='rpi4',
    system=SystemContext(
        # Omit password if user has no password
        credentials=Credentials(login='pi', password='raspberry')),
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
from pluma import Board, SystemContext, Credentials

# Control classes defined elsewhere for this example
from my_hardware import console


board = Board(
    name='my_unusual_board',
    console=console,
    login_user_match='Enter username:',
    login_pass_match='Enter password:',
    system=SystemContext(credentials=Credentials(
        login='dave',
        password='bad_password'))
)
```

If after the password is sent to the console, the `login_pass_match` is received again, it is assumed that the password was incorrect and the login has failed.
If this is not the case then the login is assumed to have succeeded, as this is the default behaviour of the Linux login prompt.  
If you know in advance what the terminal prompt is for the board, then you can provide this to the `Board` so it knows for sure the login was a success.
In other words, if we see the `prompt` after we entered the password then the login has succeeded. If not, it has failed.  
This method can be more robust, but requires additional knowledge of the board's console behaviour in advance.

```python
from pluma import Board, SystemContext, Credentials

# Control classes defined elsewhere for this example
from my_hardware import console


board = Board(
    name='my_unusual_board',
    console=console,
    system=SystemContext(
        prompt_regex=r'pi@raspberrypi:~ \$'
        credentials=Credentials(login='pi', password='raspberry'))
)
```

Often before calling the `login()` method we call the `reboot_and_validate()` method to ensure the board is booted and ready for login.
If we have defined the `Board`'s `prompt`, and during the `reboot_and_validate()` process the `prompt` was received rather than the boot string, then we know that there is no need to attempt to login.
The board is already passed the point where we'd need to login, and if we tried to login it would fail!  
To get around this issue, if `login()` is called after `reboot_and_validate()` received the `prompt` then the login is not attempted.
To know whether this is not the case you can read the board's `booted_to_prompt` property

```python
from pluma import Board, ConsoleLoginFailedError, SystemContext, Credentials

# Control classes defined elsewhere for this example
from my_hardware import console, power


board = Board(
    name='rpi4',
    console=console,
    system=SystemContext(
        prompt_regex=r'pi@raspberrypi:~ \$'
        credentials=Credentials(login='pi', password='raspberry'))
)


board.reboot_and_validate()

print(board.booted_to_prompt)
# True

# Will succeed without checking the console since we know the board has
# already booted to the terminal prompt
board.login()
```

## Logging

**Important note:** _The information below is equally applicable to all the hardware control classes, as they are able to log individually and support the logging behaviour. For example, you will see some of these options used with the `SerialConsole` class in [Tutorial: Adding a storage controller](./2-4-tutorial-storage.md)._

Top level logging is usually done via the `Board`'s `log()` method.
By default the log message will be printed, as well as being written to a temporary file.

```python
# Defined elsewhere for this example
from my_hardware import my_board

my_board.log('Hello World!')
#Hello World!
```

To see where the `Board`'s current log file is we can read the `log_file` property:

```python
print(my_board.log_file)
#/tmp/pluma/Board_2020-06-05-10-52-25.log
```

Let's check the contents of that file to ensure our "Hello World!" message was saved:

```shell
pi@raspberry:~ $ cat /tmp/pluma/Board_2020-06-05-10-52-25.log
Hello World!
```

Often it is useful to see the log updating in realtime as Pluma is running.  
We can do this with:

```shell
pi@raspberry:~ $ tail -f /tmp/pluma/Board_2020-06-05-10-52-25.log
Hello World!
```

### Moving an clearing log files

You'll notice that the log file in the last example is in the `/tmp/` directory.
This means that it is only stored in memory and will not persist across reboots.
Another thing to note is that the end of the file name is a timestamp, noting the time that Pluma's Python session started.
As a result of this, each time you run a Pluma script a new log file will be created.

This is often not the behaviour you want.
Wouldn't it be nice if we could make the log file permanent, and just append new messages to the end of the log for a new session rather than having to store many log files?

To achieve this you can change the log file location:

```python
from my_hardware import my_board

# Change the location of the log file. Append to this file if it exists
my_board.log_file = './my_board.log'

```

If you would rather your log messages aren't appended to the end of old log file, then you can clear it with the `log_file_clear()` method.

```python3
my_board.log_file = './my_board.log'
my_board.log_file_clear()
```

### Disabling logging

You may not want every message you `log()` to be printed to the console, or maybe you don't want any logs at all?

```python
from my_hardware import my_board

# Disable printing log messages to the console
my_board.log_echo = False

# Disable logging altogether
my_board.log_on = False
```

### Improving log output

So we have logging working, but it would be good to have some additional information in the logs, like timestamps for instance.
The `Board` class has various properties and methods to change how our log messages are formatted.

```python
from my_hardware import my_board

my_board.log('Hello world!')
#Hello world!

# Add a name to distinguish what object wrote a given log message
#   You might want to set this to the name you gave when creating your Board
my_board.log_name = 'Raspberry Pi 4b'
my_board.log('Hello world!')
#Raspberry Pi 4b: Hello World!

# Add a timestamp each log message
my_board.log_time = True
my_board.log('Hello world!')
#05-06-20 12:34:58 Raspberry Pi 4b: Hello World!

# Change the timestamp format
#   For more information on format strings see:
#   https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
my_board.log_time_format = 'The date is %d %m, %Y and the time is %H hours, %M mins, and %S seconds'
#The date is 05 06, 2020 and the time is 12 hours, 37 mins, and 44 seconds Raspberry Pi 4b: Hello World!
```

As you can see there are a lot of options for customising the log output, and they can all be used together if that's what you want.

### Change how individual log messages are displayed

It is also possible to change how an individual log message is displayed.
The per-message options below override any global setting from the previous section.

```python
from my_hardware import my_board

# Change the color of the log message is printed to stdout
my_board.log('Hello', color='red')

# Display the message printed to stdout in **bold**
my_board.log('Hello', bold=True)

# Force logging to console even if my_board.log_echo is set to False
my_board.log('Hello', force_echo=True)

# Force logging this individual message to a different file
#   May be useful for logging critically important messages elsewhere
my_board.log('Hello', force_log_file='./high_priority_messages.log')
```

For changing the color of the log message, the following `color` strings are supported:

- black
- blue
- cyan
- green
- purple
- red
- white
- yellow

___

<< Previous: [Tutorial: Adding a storage controller](./2-4-tutorial-storage.md) |
Next: [Tutorial: Test Framework](./3-tutorial-test-framework.md) >>
