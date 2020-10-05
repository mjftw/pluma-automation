
# Tutorial: Hardware Control - Adding a Console Controller

In order to interact with a board's console, we need to create a console controller.

There are different console controllers for different transport types, but they all share a common base `ConsoleBase`.  
This common base means that once the console is defined, the rest of the program doesn't need to know what kind of console it is.

## Example: Console over USB -> UART cable

A common use case is to interact with a board's debug UART using a USB to UART cable.

```python
from pluma import SerialConsole

console = SerialConsole(
    port='/dev/ttyUSB0'
    baud=115200
)
```

## Example: Console over SSH

We may find that we cannot connect a debug UART cable to our DUT to monitor its console, but we can connect using SSH.  
This can be achieved using the HostConsole class.
This class runs a command on the host machine, and interacts with it as if it were a console.  

We could use this to run a native bash console on our host.  
Try it out for yourself in an interactive Python interpreter:

```shell
dev@labhost:~ $ ipython3

In [1]: from pluma import HostConsole

In [2]: console = HostConsole('/bin/bash')

In [3]: console.interact()

dev@labhost:~ $ pwd
/home/dev/

# Press Ctrl-D to exit the interactive shell

In [4]:
```

The console's `interact()` method lets you take interactive control of the DUT console. This can be very handy for debugging as it allows you to take interactive control of the console after Pluma has been using it for automation.

HostConsole is a very flexible console class, and we can use it to run a bash shell on our DUT over SSH as well:

```python
from pluma import HostConsole

console = HostConsole('ssh pi@raspberrypi.local /bin/bash')
```

This works best if you can connect to the DUT over SSH without needing to enter a password. The easiest way to do this is using the tool [ssh-copy-id][ssh-copy-id].

See [Console Classes](../quick-start-guide/console-classes.md) for all the console types supported.

[ssh-copy-id]: https://www.ssh.com/ssh/copy-id

## Sending commands

The main use for the console classes is to send commands to our DUT.  

Try out the following:

```python
from pluma import HostConsole

console = HostConsole('ssh dut-user@dut-host /bin/bash')

console.send('cd ~')
console.send('echo "Hello World!" > pluma-test.txt')

console.interact()
pi@raspberry:~ $
pi@raspberry:~ $ cat pluma-test.txt
Hello World!
```

## Searching for matches

### Exact matches

Another useful feature of the console is to send a command and check the response against some expected options.

As an example, lets use the console to find out what machine architecture our DUT is using the `uname -m` command.

```python
from pluma import HostConsole

console = HostConsole('ssh dut-user@dut-host /bin/bash')

machines = ['arm', 'i386', 'x86_64']
received, matched = console.send_and_expect('uname -m', match=machines)
# `received` gets everything before a match was found
# `matched` is the match string that was found

if matched == 'arm':
    print('Target is ARM based')
elif matched == 'i386':
    print('Target is an x86 machine')
elif matched == 'x86_64':
    print('Target is an x64 machine')
elif not matched:
    print('Unknown machine type')

```

The console will stop searching as soon as it finds a string that matches what it is looking for, and later matches will not be found.

### Regular expressions

The strings that are used to find matches with `console.send()` are actually regular expressions.
This lets us do some more useful things.

As an example, let's use regular expressions to extract the system time from the result of running the `date` command.

```shell
dev@labhost:~$ date
Thu  7 May 20:24:47 BST 2020
```

```python
from pluma import HostConsole

console = HostConsole('/bin/bash')
__, matched = console.send_and_expect('date', match='[0-9]+:[0-9]+:[0-9]+')

print(matched)
# 20:24:49
```

If you are unfamiliar with regular expressions, you can find many guides online. [RegexOne][regexone] is a great place to start.

You should be careful using regex patterns though as they may not do exactly as you expect.
See [Pexpect documenatation][pexpect] for more info (The search is done using the pexpect library).

[regexone]: https://regexone.com/
[pexpect]:https://pexpect.readthedocs.io/en/stable/overview.html#find-the-end-of-line-cr-lf-conventions

## Common problems

This works well, but can have some problems.
Try running this command on you DUT:

```shell
dev@labhost:~ $ ssh pi@raspberrypi.local
pi@raspberry:~ $ test 5 -gt 6 && echo "5 > 6" || echo "5 < 6"
5 < 6
```

This command checks if 5 is greater than 6, and should report "5 < 6" as expected.

Now let's try the same command via the console.

```python
from pluma import HostConsole
console = HostConsole('ssh pi@raspberrypi.local /bin/bash')

command = 'test 5 -gt 6 && echo "5 > 6" || echo "5 < 6"'
answers = ['5 > 6', '5 < 6']

received, matched = console.send_and_expect(command, match=answers)

print(matched)
# 5 > 6
```

Doing this we find that "5 > 6". Clearly something has gone wrong.  
Lets see if we can work out what happened by seeing what we received before the match.

```python
print(received)
# '"\r\n\r\ntest 5 -gt 6 && echo "'
```

From this you can see that what we matched wasn't actually the answer to the command we sent, but part of the command itself!
This happens because the console that we are attached to is echoing back everything we send to it.

Let's see what's left in the console's receive buffer from after the last match.  
By default the receive buffer is flushed before sending a command, but we can disable this with `flush_before=False`.  
If we don't have anything we want to match against, but still want to see the result of the command we send we can use `receive=True`.
This will cause the console to wait until no more data is being sent and then return everything it received.

Sending a command is also optional, and a newline will be sent by default if no command is specified, we can prevent this with `send_newline=False`.

```python
received, matched = console.send_and_expect(flush_before=False, send_newline=False, match=['expected output'])
received = console.send_and_read(flush_before=False, send_newline=False)
console.send('', flush_before=False, send_newline=False)

print(received)
# 5 < 6\r\n
```

Here we can see the answer we were looking for.  
The same result can be achieved more simply by reading the console's receive buffer using the `read_all` method, but without clearing it.

```python
buffer_contents = console.read_all(preserve_read_buffer=True)

print(buffer_contents)
# 5 < 6\r\n
```

One way to get around this is to disable echo on the console. Disabling the prompt can be helpful too.

```python
from pluma import HostConsole
# Note: ssh -t is required in order to use the stty command over SSH
console = HostConsole('ssh -t pi@raspberrypi.local /bin/bash')

# Disable the prompt
console.send('export PS1=')
# Disable echo
console.send('stty -echo')

command = 'test 5 -gt 6 && echo "5 > 6" || echo "5 < 6"'
answers = ['5 > 6', '5 < 6']

received, matched = console.send_and_expect(command, match=answers)

print(matched)
# 5 < 6
```

## Logging

An easier way to diagnose what went wrong in the last example would be to have a look at the console's log.  
The console has two log files, one for the console class and another for the raw sent/received data.

In the console log we can see everything the console has sent and received, as well as control sequences indicating everything that it has searched for, matched, and flushed.
This can be very useful for diagnosing when something has gone wrong!
The console log is only updated when an operation on the console class takes place.

The raw log file contains an up to date log of everything that has been sent on the console to date, without control information.

All Pluma hardware control classes have a log file, but only the console classes have a raw log file.

Both default to being stored in a temporary file in `/tmp/pluma`, but you can change the logfile locations by setting the attributes on the console instance.

```python
console.raw_logfile = './raw_console_data.log'
console.log_file = './console_control.log'
```

If setting a logfile in a non default location, it is useful to clear the logs at the start of your test script as the old data from previous tests is not cleared by default.

```python
console.raw_logfile_clear()
console.log_file_clear()
```

It can be useful to have a live view of how Pluma is interacting with a board as it runs. To do this you can run the following command in a separate shell:

```shell
tail -f ./raw_console_data.log
```

If you have many different log files in your logs directory, then you can use this to follow the newest one:

```shell
tail -f $(ls -t | grep '.log' | head -n 1)
```

## Diagnosing problems using the log files

Let's repeat the problematic previous example and have a look at the log files.

```python
from pluma import HostConsole
console = HostConsole('ssh pi@raspberrypi.local /bin/bash')

command = 'test 5 -gt 6 && echo "5 > 6" || echo "5 < 6"'
answers = ['5 > 6', '5 < 6']

received, matched = console.send_and_expect(command, match=answers)
print(console.log_file)

# Flush the receive buffer so we can see all received data in the console log
console.read_all()

print(console.log_file)
#/tmp/pluma/HostConsole_2020-05-07-19-25-04.log
```

Looking at the log file we can see what went wrong.

```shell
dev@labhost:~ $ cat /tmp/pluma/HostConsole_2020-05-07-19-25-04.log
<sent>>b'test 5 -gt 6 && echo "5 > 6" || echo "5 < 6"'<</sent>>
Waiting up to 5s for patterns: ['5 > 6', '5 < 6']...
<<received>>test 5 -gt 6 && echo "<<matched expects=['5 > 6', '5 < 6']>>5 > 6<</matched>><</received>>
<<sent>>b''<</sent>>
Waiting for quiet... Waited[0.0/3.0s] Quiet[0.0/0.3s] Received[7B]...
Waiting for quiet... Waited[0.1/3.0s] Quiet[0.1/0.3s] Received[7B]...
Waiting for quiet... Waited[0.2/3.0s] Quiet[0.2/0.3s] Received[7B]...
Waiting for quiet... Waited[0.3/3.0s] Quiet[0.3/0.3s] Received[7B]...
<<flushed>>5 < 6
<</flushed>>
```

___

<< Previous: [Tutorial set: Hardware Control](./2-tutorial-hardware-control.md) |
Next: [Tutorial: USB Devices](./2-2-tutorial-usb.md) >>
