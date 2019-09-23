#!/bin/bash
#
# Dependency installer script for Debian based Linux distributions
#

# Install as sudo if sudo command installed, and user is not root
SUDO=""
if [ ! -z "$(which sudo)" -a "$UID" != "0" ]; then
    SUDO="sudo"
fi

# LibUSB required for PyFTDI library used by SDWire
$SUDO apt install -y libusb-1.0 python3 python3-pip graphviz

# Install Python libraries
pip3 install -r requirements.txt