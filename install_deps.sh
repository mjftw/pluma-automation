#!/bin/bash
#
# Dependency installer script for Debian based Linux distributions
#

# LibUSB required for PyFTDI library used by SDWire
sudo apt install -y libusb-1.0 python3 python3-pip graphviz

# Install Python libraries
pip3 install -r requirements.txt