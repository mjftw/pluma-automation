# Tutorials

**Follow structure from GStreamer Tutorials:**
https://gstreamer.freedesktop.org/documentation/tutorials/index.html?gi-language=c


## Welcome to the Automation Lab tutorials!

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

- Using the TestRunner
- Writing a custom test
- Using the TestController
  - Multiple test iterations

#### Build an image and check it boots

- Build Raspberry Pi image using Yocto
- Flash image to SD Card using SD Wire
- Insert SD Card into target
- Power on target
- Check target boots & measure boot time

#### Monitor target performance

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

### Prerequisites

### Source code

___

<< Previous: [Quick Start Guide](../quick-start-guide/1-introduction.md) | 
Next: [Tutorial: Hardware Control](./2-tutorial-hardware-control.md) >>
