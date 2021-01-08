#!/bin/bash

# Install as sudo if sudo command installed, and user is not root
SUDO=""
if [ ! -z "$(which sudo)" -a "$UID" != "0" ]; then
    SUDO="sudo"
fi

install_pyright() {
    if [ -z "$(which npm)" ]; then
        echo "Pyright requires npm to be installed. Please do this first."
        exit 1
    fi

    echo "Installing pyright (Python static type checker) npm package globally..."
    $SUDO npm install -g pyright
}

install_pyright