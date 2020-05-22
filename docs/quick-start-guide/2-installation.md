# Installation

In order to use the packages farmcore, farmtest, and farmutils you will first need to install them all as Python packages.
This is done using the Python package manager pip3.  
There are also some Linux system level dependencies, which are satisfied using Debian packages.  
This does mean that the codebase is currently only tested to work on Debian based Linux distributions, such as Ubuntu 18.04.
It should be possible to satisfy these dependencies on a different distribution, but no work has been done to test this.  

An install scrip [install.sh](install.sh) is provided.  
This script will install all of the required Debian packages, and install farmcore, farmtest, and farmutils as pip packages.  

It can be used as below:

``` shell
./install.sh
```

By default the modules will be installed as immutable packages, and edits in this local directory will not affect the installed packages.  
This is what we would want for a normal user, who will be using these packages as a library to develop against.
It is safe to rerun this install script to update the installed packages from local changes, but not recommended.

If you are planning to develop the packages, and want your local source changes in this directory to take immediate affect, use the `-d` flag.

```shell
./install.sh -d
```

When installing with this option, local changes immediately take affect, and any Python scripts importing farmcore, farmutils, or farmtest will be affected.
It is recommended to only use this option if you are actively developing these packages, and not for a normal install!
___

<< Previous: [Introduction](./1-introduction.md) | 
Next: [Hardware Overview](./3-hardware_overview.md) >>
