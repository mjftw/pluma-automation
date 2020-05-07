# Witekio Automation Lab

This all documentation, and code is currently under development, and may be subject to change, so use caution.

A draft coding guide for developers can be found here: [Style Guide](./docs/style-guide.md).

A good place to start for new users is the [Quick Start Guide](./docs/quick-start-guide/1-introduction.md) Guide and [Tutorials](./docs/tutorials/1-tutorial-introduction.md)

## Installation

In order to use the packages farmcore, farmtest, and farmutils you will first need to install them all as Python packages.
This is done using the Python package manager pip3.  
There are also some Linux system level dependencies, which are satisfied using Debian packages.  
This does mean that the codebase is currently only tested to work on Debian based Linux distributions, such as Ubuntu 18.04.
It should be possible to satisfy these dependencies on a different distribution, but no work has been done to test this.  

An install scrip [install.sh](install.sh) is provided.  
This script will install all of the required Debian package, and install farmcore, farmtest, and farmutils as pip packages.  

It can be used as below:

``` shell
./install.sh
```

By default the modules will be installed as immutable packages, and edits in this local directory will not affect the installed packages.  
This is what we would want for a normal user, who will be using these packages as a library to develop against.
It is safe to rerun this install script to update the installed packages from local changes, but not recommended.

If you are planning to develop the packages, and want your local source changes in this directory to take immediate affect, use the `--dev` flag.

```shell
./install.sh --dev
```

When installing with this option, local changes immediately take affect, and any Python scripts importing farmcore, farmutils, or farmtest will be affected.
It is recommended to only use this option if you are actively developing these packages, and not for a normal install!

## Using the packages

Once you have run the install script [install.sh](install.sh) you should be able to import and use the farmcore, farmtest, and farmutils in your Python scripts.

```python
# my_project_file.py
import farmcore
import farmtest
import farmutils
```

## Email Settings

To use the email functionality of the lab you should create an email settings file.  
This file should be in the root directory of this repository and be named `email_settings.json`.  
This file should be json formatted as shown in the example file below:

\<farm-core>/email_settings.json:

```json
{
    "smtp": {
        "email": "lab@witekio.com",
        "password": "reallybadpassword",
        "server": "smtp.office365.com",
        "delay": 587
    },
    "maintainers": [
        "john_smith@domain.com",
        "maxime_richard@domain.com"
    ]
}
```

The `"smtp"` section is required for sending emails, and the email address in the `"maintainers"` section will be used for sending exception reports. You must specify at least one maintainer.  
The options `"server"` and `"delay"` are optional, and the above values will be used if these settings are not present.

This settings file is _technically_ optional as you can specify username and passwords in the relevant class method and function calls, but anything that sends automated emails (such as error reports) will not work without it.  
Adding this file will make your life easier.
