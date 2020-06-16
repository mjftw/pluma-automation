# Witekio Automation Lab

The Automation Lab is a tool designed to perform black box testing of embedded hardware; designed to be as lightweight as possible!

At it's core it enables programmatic hardware control of many supported devices to control a board's power, console, storage, and more.
This package is named `farmcore`.

On top of the hardware control library sits a testing framework `farmtest`, which automates the hardware control to run testing of many flavours (regression, soak, feature, etc). This package is entirely optional.
`farmcore` still works well without it, and can be easily integrated with other testing frameworks and CI/CD tools such as [Pytest](https://docs.pytest.org/) or [Buildbot](https://buildbot.net/).

Finally we have `farmutils`, a utilities library to provide additional features such as email reporting or downloading code from `git` repositories.

System features include:

* [Automated testing framework](docs/tutorials/3-tutorial-test-framework.md)
* [A Docker container to run your tests in](docs/quick-start-guide/2-install-and-run.md)
* [Draw a plot of your USB tree](docs/tutorials/2-2-tutorial-usb.md)
* [Email reporting](docs/tutorials/4-1-tutorial-email.md)
* Flexible and extensible test scheduler
* Generate test reports with automatically formatted results and graphs
* Make and receive phone calls and text messages
* Read in-circuit voltage and current values

Hardware control features include:

* [Turn boards on and off remotely](docs/tutorials/2-3-tutorial-power.md)
* [Built-in boot test](docs/tutorials/2-5-tutorial-board.md)
* [Send commands to a board's console](docs/tutorials/2-5-tutorial-board.md)
* [USB relay control](docs/tutorials/2-3-tutorial-power.md)
* [SD card multiplexing](docs/tutorials/2-4-tutorial-storage.md)
* [Smart USB device detection](docs/tutorials/2-2-tutorial-usb.md)
* ... and much more!

The Automation Lab is designed to be easily extensible. If your smart plug, clever kettle, or hardware doodar isn't supported then you can probably integrate it without too much work.
Just be sure to raise a pull request with your shiny new feature ;).

## Getting Started

The Automation Lab has a documentation site, hosting all the documents below, as well as an up to date API guide.  
It can be found at [http://labdocs](http://labdocs).

**Note:** _The docs site is only accessible from within the Witekio network_

To get up and running quickly, check out the [Quick Start Guide](./docs/quick-start-guide/1-introduction.md).  
Look at the [Tutorials](./docs/tutorials/1-tutorial-introduction.md) for guidance and examples on how to use the Automation Lab in your project.

## Installation

The Automation Lab can be run natively, or using Docker.

For native installation, just run the `install.sh` script.
This will install all the required system packages, then install the `farm-core` python packages.
This installer assumes you are running a debian based Linux distro, such as Ubuntu or Raspian.

```shell
./install.sh
```

To run with Docker you must first build the container.

```shell
make docker-build
```

**Note:** _For ARM based systems you must use thr `docker-build-arm` target instead_.

Run the container with your project:

```shell
make docker-run-privileged PROJECT_DIR=/path/to/my/project PROJECT_SCRIPT=myscript.py
```

Where `PROJECT_DIR` is a directory containing all python scripts needed to run, and `PROJECT_SCRIPT` is the script to run from within that directory.

**Note:** _For ARM based systems you must use the `docker-run-privileged-arm` target instead_.

For more detailed instructions, see the [Install and Run](./docs/quick-start-guide/2-install-and-run.md) section of Quick Start Guide.
Here you'll find instructions on how to run the Automation Lab with Docker.

## Using the packages

Once you've installed the lab (or run the Docker container), you should be able to import and use the farmcore, farmtest, and farmutils in your Python scripts.

```python
# my_project_file.py
import farmcore
import farmtest
import farmutils

# Create a Board (full Board arguments not shown)
my_board = farmcore.Board('My board')

# Send a command to the board
my_board.console.send('uname -a')

# Turn the board off
my_board.power.off()
```

The above code is just for demonstration, for working code examples check out the [Tutorials](docs/tutorials/1-tutorial-introduction.md).

## Contributing

If you would like to contribute to developing the Automation Lab then check out our [Contributing Guide](./docs/how-to-contribute.md) to find out how.

We also have a code style guide for you to read before you begin development: [Style Guide](./docs/style-guide.md)

## Licensing

The Automation Lab is released under a [GPLv3 License](LICENSE.txt).
