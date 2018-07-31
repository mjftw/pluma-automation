# Witekio Lab Quick Start Guide
This guide is intended to give an overview of the hardware and software in the Witekio Lab, and how to use it.  
For the purpose of this guide, we will use the Witekio UK farm as an example.

- [Witekio Lab Quick Start Guide](#witekio-lab-quick-start-guide)
    - [Farm Hardware Overview](#farm-hardware-overview)
        - [Farm host](#farm-host)
            - [Host PC](#host-pc)
            - [Host Hub](#host-hub)
            - [USB Relay](#usb-relay)
            - [PDU](#pdu)
        - [Farm Board](#farm-board)
            - [Board](#board)
            - [Board Hub](#board-hub)
            - [SD Mux](#sd-mux)
    - [Farm software overview](#farm-software-overview)
        - [Installation](#installation)
    - [Tutorials](#tutorials)
        - [Tutorial 1: Writing a farm script](#tutorial-1-writing-a-farm-script)
        - [Tutorial 2: Sending commands over serial](#tutorial-2-sending-commands-over-serial)
        - [Tutorial 3: Using the SDMux to transfer files to a board](#tutorial-3-using-the-sdmux-to-transfer-files-to-a-board)
        - [Tutorial 4: Sending email reports](#tutorial-4-sending-email-reports)
        - [Tutorial 5: Adding a board to the farm](#tutorial-5-adding-a-board-to-the-farm)
---
## Farm Hardware Overview
In this section we will look at the hardware setup of the farm.

The hardware setup can roughly be divided into the following blocks:

- [Farm Host](#farm-host)
    - [Host PC](#host-pc)
    - [Host Hub](#host-hub)
    - [USB Relay](#usb-relay)
    - [PDU](#pdu)
- [Farm Board](#farm-board)
    - [Board](#board)
    - [Board Hub](#board-hub)
    - [SD Mux](#sd-mux)

![Hardware block diagram](hardware_block_diagram.svg)  
*Hardware block diagram shows how each of the system components are connected.  
Only two boards are shown, but any number could be added.  
Only one PDU and USB Relay are pictured, but again, any number could be added.*

### Farm host
The farm host represents all of the hardware components that do not need a seperate instance for each board.

#### Host PC
The Host PC is the Linux machine that all other farm hardware is connected to and its responsibilities include:
- Controlling each boards hardware
- Creating and sending any data graphs and reports that are needed
- Handling remote access to the boards

#### Host Hub
This is the root USB hub to which all other farm related USB devices are connected.  
Most importantly, it acts as a common upstream USB device that each of the board hubs are connected to.  
Any USB devices that do not require a seperate instance per board are also connected to the Host PC via this hub.  
An example of one such device is a USB Relay, which has its serial port connected to the Host Hub via a UART to USB converter, as shown in the section [Farm Hardware Overview](#farm-hardware-overview).

#### USB Relay
This is a device that is conected to the [Host Hub](#host-hub).  
It has 4 output ports each of which comprise of a common line, and an A and B line.
By sending commands over serial, the common line of each output can be mechanically connected to either the A or B line.  
The model used by the Witekio Lab UK is the DLP-IOR4 by FTDI, and more detailed information can be found [here](http://www.ftdichip.com/Support/Documents/DataSheets/DLP/dlp-ior4-ds-v12.pdf).

In its current configuration, the farm uses this to toggle the select line of the [SD Mux](#sd-mux) connected to each board.  
However, this is by no means the only use for a USB Relay, and it could be used to switch any line up to a maximum power rating of 60W per relay.

#### PDU
The PDU is a switched rack Power Distribution Unit, to which each of the boards are connected.  
It is controlled over the network using the [Telnet protocol](https://en.wikipedia.org/wiki/Telnet), and is capible of indipendently controlling whether each of it's 8 output ports provide power.  
It's primary use is to allow a board to be turned on and off remotely via software.  
The model of PDU used in the Witekio Lab UK is the AP7920 by APC, and a manual can be found [here](http://www.apc.com/salestools/ASTE-6Z6K56/ASTE-6Z6K56_R0_EN.pdf).

### Farm Board
This represents all of the hardware that is required to have a seperate instance per board added to the farm.  

#### Board
The Board refers to our design under test.  
A common configuration for a board is to have an SD card slot for data storage, and a serial console for control. This therefore what the current iteration of the Witekio Lab's farm setup expects.  
The power supply of each board is connected to a port on the [PDU](#pdu) in order to allow it to be turned on and off remotely.

#### Board Hub
Each board has an associated board hub, to which all USB devices for interacting with that board are connected.  
The board hub should be connected upstream to the [Host Hub](#host-hub) in order to allow the [Host PC](#host-pc) to control the board.  
It is essential that one board hub is not connected downstream of another, as this causes issues for when automatically detecting which hardware is associated with a given board.  
Wherever a device is able connected via USB, it should be, as this allows a common interface for the [Host PC](#host-pc) to control the device.
For example, the serial port of each board is connected to the Board Hub via a UART to USB conversion cable.

#### SD Mux
This is a device which holds a micro SD Card, and is capible of switching it from being connected to its "slave" or "host" port, depending on the value of its "select" input.
The select line is toggled by using a [USB Relay](#usb-relay).

This is a custom device created by Witekio UK, but in future it may be replaced with off the shelf, or open source hardware.

Currently the power supply for each SD Mux is connected to the PDU. This is done in order to be able to reboot the device, should it experience functional issues.

---
## Farm software overview
In this section we will show how the hardware configuration of the farm is represented in software.

**[Software description and diagrams]**

### Installation
In this section we will look at how to download and install the Witekio Lab's farm scripts.

---
## Tutorials
In these tutorials we will demonstrate how to use the Witekio Lab's Python scripts.  
We will start with simple functionality, such as restarting a board, and work our way up to more complex functionality, such as sending email reports.

### Tutorial 1: Writing a farm script
In this tutorial we will write a farm script to demonstrate the following:
- Set up our farm script environment
- Get a board instance
- Reboot the board

_See [example_1.py](examples/example_1.py) for the completed script._  
**[Tutorial content]**

### Tutorial 2: Sending commands over serial
In this tutorial we will a basic farm script to demonstrate the following:
- Find a boards prompt
- Send a command over serial
- Wait for the command to finish execution
- Print the result

_See [example_2.py](examples/example_2.py) for the completed script._  
**[Tutorial content]**

### Tutorial 3: Using the SDMux to transfer files to a board
In this tutorial we will a basic farm script to demonstrate the following:
- Switch a board's SD card to the farm host
- Mount the SD card and copy a file to it
- Switch SD card back to the board
- Print the contents of the file over serial

_See [example_3.py](examples/example_3.py) for the completed script._  
**[Tutorial content]**

### Tutorial 4: Sending email reports
In this tutorial we will write a farm script to demonstrate the following:
- Copy a binary to a board
- Run the binary and store the result
- Email the result

_See [example_4.py](examples/example_4.py) for the completed script._
**[Tutorial content]**

### Tutorial 5: Adding a board to the farm
In this tutorial we will look at how to:
- Add a new board to the farm
- Represent this change in software

**[Tutorial content]**