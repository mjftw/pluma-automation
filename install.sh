#!/bin/bash
#
# Installer script for Debian based Linux distributions
#
set -u
set -e

install_as_dev=0
answer_all=""

function display_help {
            echo "Usage:"
            echo "  $0 [-d] [-h] [-y] [-n]"
            echo ""
            echo "  -d Install as pluma developer. This causes changes to the local"
            echo "     pluma directory to be imported on 'import pluma' etc."
            echo "     Do not enable this option unless you plan to modify pluma."
            echo "  -y Answer yes to all questions (non-interactive installer)"
            echo "  -n Answer no to all questions (non-interactive installer)"
            echo "  -h Display this info."
}

function add_group {
    group="$1"
    if [ -z "$(grep $group < /etc/group)" ]; then
        $SUDO groupadd $group
        $SUDO usermod -aG $group $(whoami)
    fi
}

function support_serial {
    echo "Adding user to dialout group (Required for USB serial control)"
    add_group dialout
}

function support_sdwire {
    $SUDO apt install -y --no-install-recommends libusb-1.0-0 libftdi-dev

    # LibUSB required for PyFTDI library used by SDWire
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

function support_uhubctl {
    $SUDO apt install -y --no-install-recommends uhubctl
    echo 'Consider adding a udev rule in "/etc/udev/rules.d/50-uhubctl.rules"
(SUBSYSTEM=="usb", ATTR{idVendor}=="<your_device_vendor>", MODE="0666"),
or running pluma as root/sudo, if required.'
}

function install_python_packages {
    echo
    echo "Installing pluma package..."

    if [ $install_as_dev -eq 1 ]; then
        # Install packages as a pluma package developer.
        # The current dir is used as the package root, and any edits made to python
        #   scripts here WILL be picked up by installed package.
        # This option is to be used when developing the pluma packages.

        python3 -m pip install --upgrade --editable "$PROJECT_ROOT"
        echo
        echo "=== Installed pluma package, editable from $PROJECT_ROOT (dev mode) ==="
    else
        # Install pluma packages as pluma package user.
        # Edits in local pluma dir will not be used by installed packages, and
        #   package must be reinstalled using script to track these changes.
        # This is what we would want for a normal user.

        python3 -m pip install --upgrade "$PROJECT_ROOT"
        echo
        echo "=== Installed pluma package ==="
    fi
}

# Install as sudo if sudo command installed, and user is not root
SUDO=""
if [ ! -z "$(which sudo)" -a "$UID" != "0" ]; then
    SUDO="sudo"
fi

# Read command line options
while getopts ":dhyn" opt; do
    case ${opt} in
    "d" )
        install_as_dev=1
        ;;
    "y" )
        answer_all="y"
        ;;
    "n" )
        answer_all="n"
        ;;
    "h" )
        display_help
        exit 0
        ;;
    \? )
        echo "Invalid option: $OPTARG" 1>&2
        display_help
        exit 1
        ;;
    : )
        echo "Invalid option: $OPTARG requires an argument" 1>&2
        display_help
        exit 1
        ;;
    esac
done
shift $((OPTIND -1))

PROJECT_ROOT="$(realpath $(dirname "$0"))"

$SUDO apt update && \
  $SUDO apt install -y --no-install-recommends \
    python3 python3-pip graphviz git sshpass

if [ "$answer_all" ==  "n" ]; then
    echo "Skipping optional config..."
elif [ "$answer_all" ==  "y" ]; then
    support_serial
    support_sdwire
    support_uhubctl
else
    echo
    read -p 'USB Serial support required? (Y/n): ' require_serial
    if [ "$require_serial" == "n" -o "$require_serial" == "N" ]; then
        echo "USB Serial support not added. Script can be rerun to enable this."
    else
        support_serial
    fi

    echo
    read -p 'SD-Wire support required? This will add new udev rules (Y/n): ' require_sdwire
    if [ "$require_sdwire" == "n" -o "$require_sdwire" == "N" ]; then
        echo "SD-Wire support not added. Script can be rerun to enable this."
    else
        support_sdwire
    fi

    echo
    read -p 'uhubctl support required (USB HUB power control)? This will add new udev rules (Y/n): ' require_uhubctl
    if [ "$require_uhubctl" == "n" -o "$require_uhubctl" == "N" ]; then
        echo "SD-Wire support not added. Script can be rerun to enable this."
    else
        support_uhubctl
    fi
fi

install_python_packages

echo
echo "Please now log out and in for changes to take affect"
