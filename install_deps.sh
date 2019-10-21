#!/bin/bash
#
# Dependency installer script for Debian based Linux distributions
#

# Install as sudo if sudo command installed, and user is not root
SUDO=""
if [ ! -z "$(which sudo)" -a "$UID" != "0" ]; then
    SUDO="sudo"
fi

PROJECT_ROOT="$(dirname "$0")"

# LibUSB required for PyFTDI library used by SDWire
$SUDO apt install -y libusb-1.0 python3 python3-pip graphviz

# Install Python libraries
pip3 install --user -r $PROJECT_ROOT/requirements.txt

# Install farm-core packages (farmcore, farmtest, farmutils)
if [ "$1" == "-d" -o "$1" == "--dev" ]; then
    # Install packages as a farm-core package developer.
    # The current dir is used as the package root, and any edits made to python
    #   scripts here WILL be picked up by installed package.
    # This option is to be used when developing the farm-core packages.

    echo "=== Installing farm-core packages (farmcore, farmtest, farmutils), editable from $PROJECT_ROOT (dev mode) ==="
    pip3 uninstall -y farm-core
    pip3 install --user --editable $PROJECT_ROOT
else
    # Install farm-core packages as farm-core package user.
    # Edits in local farm-core dir will not be used by installed packages, and
    #   package must be reinstalled using script to track these changes.
    # This is what we would want for a normal user.

    echo "=== Installing farm-core packages (farmcore, farmtest, farmutils) ==="
    pip3 uninstall -y farm-core
    pip3 install --user $PROJECT_ROOT
fi