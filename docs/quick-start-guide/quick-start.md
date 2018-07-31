# Witekio Lab Quick Start Guide
This guide is intended to give an overview of the hardware and software in the Witekio Lab, and how to use it.  
For the purpose of this guide, we will use the Witekio UK farm as an example.

- [Witekio Lab Quick Start Guide](#witekio-lab-quick-start-guide)
    - [Farm hardware overview](#farm-hardware-overview)
        - [Farm host](#farm-host)
            - [Host PC](#host-pc)
            - [Host Hub](#host-hub)
            - [APC](#apc)
        - [Farm Board](#farm-board)
            - [Board](#board)
            - [SD Mux](#sd-mux)
            - [Board Hubs](#board-hubs)
    - [Farm software overview](#farm-software-overview)
        - [Installation](#installation)
    - [Tutorials](#tutorials)
        - [Tutorial 1: Writing a farm script](#tutorial-1-writing-a-farm-script)
        - [Tutorial 2: Sending commands over serial](#tutorial-2-sending-commands-over-serial)
        - [Tutorial 3: Using the SDMux to transfer files to a board](#tutorial-3-using-the-sdmux-to-transfer-files-to-a-board)
        - [Tutorial 4: Sending email reports](#tutorial-4-sending-email-reports)
        - [Tutorial 5: Adding a board to the farm](#tutorial-5-adding-a-board-to-the-farm)
---
## Farm hardware overview
In this section we will look at the hardware setup of the farm.

The hardware setup can roughly be divided into the following blocks:
- [Farm Host](#farm-host)
    - [Host PC](#host-pc)
    - [USB Relay](#usb-relay)
    - [Host Hub](#host-hub)
    - [APC](#apc)
- [Farm Board](#farm-board)
    - [Board](#board)
    - [SD Mux](#sd-mux)
    - [Board Hub](#board-hub)

![Hardware block diagram](hardware_block_diagram.svg)
*Hardware block diagram shows how each of the system components are connected.  
Only two boards are shown, but any number could be added.*

### Farm host

#### Host PC

#### Host Hub

#### APC

### Farm Board

#### Board

#### SD Mux

#### Board Hubs

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
- Wait for the command to finish exection
- Print the result

_See [example_2.py](examples/example_2.py) for the completed script._  
**[Tutorial content]**

### Tutorial 3: Using the SDMux to transfer files to a board
In this tutorial we will a basic farm script to demonstrate the following:
- Switch a boards's SD card to the farm host
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