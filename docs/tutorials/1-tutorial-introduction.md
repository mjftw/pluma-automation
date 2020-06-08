# Tutorials

## Welcome to the Automation Lab tutorials

### Prerequisites

#### Software

In order to follow these tutorials you will need to have successfully installed the Automation Lab software.  
Check out the [Install and Run](../quick-start-guide/2-install-and-run.md) guide for instructions on how to do this.  
You can use your normal computer as the Lab host machine, although we recommended that you are running Linux.  
The Lab code is developed and tested using Ubuntu 16.04 or newer, so you may have an easier time using these distributions.

#### Hardware

You will also need an embedded platform to act as your DUT board.  
For these tutorials we will be using a Raspberry Pi 4 running [Raspian Buster][raspian] as our DUT, but you can replace this with whatever board you have on hand.  

You will also need some way to connect to the console on the DUT.  
We recommend a USB to UART debug cable, but could also use SSH for your console if the DUT is network accessible.
See [Console Classes](../quick-start-guide/console-classes.md).

It is also very useful to be able to turn the DUT on and off from Python, and a requirement for any kind of boot testing.  
For this you'll need some power control hardware. The IP Power 9258 power distribution unit is great for this, but there are alternatives.  
See [Power Classes](../quick-start-guide/power-classes.md).

If you are planning to use the SD Wire (SD card multiplexer) to put images on your DUT, make sure it can boot from SD card.
You'll also need to get hold of an SD Wire board. See [Storage Classes](../quick-start-guide/storage-classes.md).

You should be able to follow along using any of the [Supported Hardware](../supported-hardware.md) for your console, power, and storage.

[raspian]: https://www.raspberrypi.org/downloads/raspbian/

### Source code

Once the Automation Lab software is installed, you should be able to import and use the Python packages in your scripts.  
To work through the tutorials, you can create a project directory and follow along in your editor of choice.

```shell
mkdir ~/lab_projects
code ~/lab_projects/my_lab_script.py
```

The Python interactive shell is very useful when combined with the Lab, and can be used to control your DUT from the command line.
While you could use the standard Python3 shell, we recommend using [iPython3][ipython] as this has a nicer interface and lots of useful features such as auto-completion.  
The interactive shell is a great way to explore the Automation Lab's classes.

[ipython]: https://ipython.org/install.html

### Structure

These tutorials will follow the process of connecting an embedded device to the Automation Lab, performing some tests, and viewing the results.  
Each tutorial will build on the knowledge from the previous ones, and introduce some new concepts.

While the Automation Lab's main focus is automated testing, it can also be used for remote hardware control.  
We'll start by setting up our hardware control classes so that we can control a board from an interactive Python shell.

Once we have this working, we can hand control of the board over to the Lab's automated testing framework and start writing our tests.

#### Hardware control

- Using the Board class
- Adding a console controller
  - Interact
  - Sending commands
  - Searching for matches

**The rest is not yet implemented. Notes only.**

- Using the Hub class
  - Understanding USB trees
  - Find usb devices
  - View usb tree
- Adding a power controller
  - Rebooting a board
- Adding a storage controller
  - Mounting an SD Card to modify files
  - Viewing modified files on the board
- Advanced Board control
  - Login
  - Reboot and validate

#### Using the test framework

**Not yet implemented. Notes only.**

- Using the TestRunner
- Writing a custom test
- Using the TestController
  - Multiple test iterations

#### Build an image and check it boots

**Not yet implemented. Notes only.**

- Build Raspberry Pi image using Yocto
- Flash image to SD Card using SD Wire
- Insert SD Card into target
- Power on target
- Check target boots & measure boot time

#### Monitor target performance

**Not yet implemented. Notes only.**

- Download application source via git (E.g. calculate prime numbers)

```C
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
  int n, i=3, c, count;

  if (argc < 2) {
    printf("Must give number of primes to calculate\n");
    exit(1);
  }
  n = atoi(argv[1]);

  if (n >= 1) {
    printf("First %d prime numbers are:\n",n);
    printf("2\n");
  }

  for (count = 2; count <= n;) {
    for (c = 2; c <= i - 1; c++) {
      if (i%c == 0)
        break;
    }
    if (c == i) {
      printf("%d\n", i);
      count++;
    }
    i++;
  }

  return 0;
}
```

- Build the application (maybe build natively on target for simplicity)
- Copy application/source to target via SCP
- Measure how long application takes for different inputs

```python
n_primes = 5000
cmd =f'{ N_PRIMES={nprimes} ; /usr/bin/time -f "$N_PRIMES, %e" ./calculate_primes.o $N_PRIMES; } 2>&1 1>/dev/null'
```

```shell
{ N_PRIMES=5000 ; /usr/bin/time -f "$N_PRIMES, %e" ./calculate_primes.o $N_PRIMES; } 2>&1 1>/dev/null

primes_found=5000, seconds_taken=0.27
```

- Copy file to host
- Plot data in graph
- Send graph via email

___

<< Previous: [Quick Start Guide](../quick-start-guide/1-introduction.md) |
Next: [Tutorial: Hardware Control](./2-tutorial-hardware-control.md) >>
