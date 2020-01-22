# Automation Lab Supported Hardware
**===== IN DEVELOPMENT =====**

- [Automation Lab Supported Hardware](#automation-lab-supported-hardware)
  - [Automation Hosts](#automation-hosts)
    - [Linux PC](#linux-pc)
    - [Raspberry Pi 4](#raspberry-pi-4)
  - [Power](#power)
    - [IP Power](#ip-power)
    - [APC](#apc)
  - [Storage](#storage)
    - [SD Wire](#sd-wire)
  - [Relays](#relays)
    - [USB Relay](#usb-relay)
  - [Measurement](#measurement)
    - [Multimeter](#multimeter)
  - [Planned](#planned)
    - [Saleae Logic Analyzer](#saleae-logic-analyzer)
    - [RS RS3005P Bench Power Supply](#rs-rs3005p-bench-power-supply)

## Automation Hosts
### Linux PC
### Raspberry Pi 4
Single board ARM based computer. 
[Documentation](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/specifications/)

## Power
### IP Power
IP Power 9258S
[Documentation](http://www.aviosys.com/downloads/manuals/power/9258S-T-SP-TP%20manual%20-V5.01.pdf)

### APC
The APC AP7920 is a switched rack Power Distribution Unit.  
It is controlled over the network using the [Telnet protocol](https://en.wikipedia.org/wiki/Telnet), and is capable of independently controlling whether each of it's 8 output ports provide power.  
[Documentation](http://www.apc.com/salestools/ASTE-6Z6K56/ASTE-6Z6K56_R0_EN.pdf).

## Storage
### SD Wire
[Documentation](https://wiki.tizen.org/SDWire)

## Relays
### USB Relay
The DLP-IOR4 is a USB connected 4 port mechanical relay by FTDI.  
Each port comprise of a common line, which can be connected to either the A or B outputs.  
By sending commands over serial, the common line of each output can be mechanically connected to either the A or B line.  
[Documentation](http://www.ftdichip.com/Support/Documents/DataSheets/DLP/dlp-ior4-ds-v12.pdf).

## Measurement
### Multimeter
TTI 1604

[Datasheet](http://www.farnell.com/datasheets/306488.pdf)
[Communications Protocol](https://docs-emea.rs-online.com/webdocs/001c/0900766b8001c784.pdf)

## Planned
### Saleae Logic Analyzer
### RS RS3005P Bench Power Supply