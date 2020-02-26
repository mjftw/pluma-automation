#!/bin/bash
#
# Installer script for Debian based Linux distributions
#

function add_group {
    group="$1"
    if [ -z "$(groups | grep $group)" ]; then
        $SUDO groupadd $group
        $SUDO usermod -aG $group $USER
    fi
}

function support_serial {
    echo "Adding user to dialout group (Required for USB serial control)"
    add_group dialout
}

function support_sdwire {
    # LibUSB required for PyFTDI library used by SDWire
    $SUDO apt install -y libusb-1.0

    echo
    echo "Adding udev rules required for FTDI devices (E.g. SD Wire)"
    echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6001", GROUP="plugdev", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6011", GROUP="plugdev", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", GROUP="plugdev", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", GROUP="plugdev", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6015", GROUP="plugdev", MODE="0666"' | $SUDO tee /etc/udev/rules.d/11-ftdi.rules
    echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", ATTR{idProduct}=="6001", GROUP="plugdev", MODE="0666"' | $SUDO tee /etc/udev/rules.d/11-sdwire.rules

    # Tell udev about to reload new rules
    $SUDO udevadm control --reload-rules
    $SUDO udevadm trigger

    echo "Adding user to plugev group (Required for FTDI device control E.g. SD Wire)"
    add_group plugdev
}

function install_python_packages {
    echo
    echo "Installing farm-core packages (farmcore, farmtest, farmutils)..."
    if [ "$1" == "-d" -o "$1" == "--dev" ]; then
        # Install packages as a farm-core package developer.
        # The current dir is used as the package root, and any edits made to python
        #   scripts here WILL be picked up by installed package.
        # This option is to be used when developing the farm-core packages.

        pip3 uninstall -y farm-core
        pip3 install --user --editable $PROJECT_ROOT
        echo
        echo "=== Installed farm-core packages (farmcore, farmtest, farmutils), editable from $PROJECT_ROOT (dev mode) ==="
    else
        # Install farm-core packages as farm-core package user.
        # Edits in local farm-core dir will not be used by installed packages, and
        #   package must be reinstalled using script to track these changes.
        # This is what we would want for a normal user.

        pip3 uninstall -y farm-core
        pip3 install --user $PROJECT_ROOT
        echo
        echo "=== Installed farm-core packages (farmcore, farmtest, farmutils) ==="
    fi
}

# Install as sudo if sudo command installed, and user is not root
SUDO=""
if [ ! -z "$(which sudo)" -a "$UID" != "0" ]; then
    SUDO="sudo"
fi

PROJECT_ROOT="$(realpath $(dirname "$0"))"

$SUDO apt install -y python3 python3-pip graphviz

support_serial
support_sdwire
install_python_packages

echo
echo "Please now log out and in for changes to take affect"
