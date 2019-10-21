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
pip3 install --user -r requirements.txt

# Install farm-core packages (farmcore, farmtest, farmutils)
if [ "$1" == "-d" -o "$1" == "--dev" ]; then
    echo "=== Installing farm-core packages (farmcore, farmtest, farmutils), editable from $PWD (dev mode) ==="
    pip3 uninstall -y farm-core
    pip3 install --user --editable .
else
    echo "=== Installing farm-core packages (farmcore, farmtest, farmutils) ==="
    pip3 uninstall -y farm-core
    pip3 install --user .
fi