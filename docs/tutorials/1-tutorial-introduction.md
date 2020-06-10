# Welcome to the Automation Lab Tutorials

## Prerequisites

### Software

In order to follow these tutorials you will need to have successfully installed the Automation Lab software.  
Check out the [Install and Run](../quick-start-guide/2-install-and-run.md) guide for instructions on how to do this.  
You can use your normal computer as the Lab host machine, although we recommended that you are running Linux.  
The Lab code is developed and tested using Ubuntu 16.04 or newer, so you may have an easier time using these distributions.

### Hardware

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

## Source code

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

## Structure

These tutorials will follow the process of connecting an embedded device to the Automation Lab, performing some tests, and viewing the results.  
Each tutorial will build on the knowledge from the previous ones, and introduce some new concepts.

While the Automation Lab's main focus is automated testing, it can also be used for remote hardware control.  
We'll start by setting up our hardware control classes so that we can control a board from an interactive Python shell.

Once we have this working, we can hand control of the board over to the Lab's automated testing framework and start writing our tests.

## Tutorial sets

Each of the tutorials are organised into sets of related content, we recommend reading them in the following order.

1. [Tutorial: Hardware Control](./2-tutorial-hardware-control.md)
1. [Tutorial: Test Framework](./3-tutorial-test-framework.md)
1. [Tutorial: Reporting](./4-4-tutorial-reporting.md)

___

<< Previous: [Quick Start Guide](../quick-start-guide/1-introduction.md) |
Next: [Tutorial: Hardware Control](./2-tutorial-hardware-control.md) >>
