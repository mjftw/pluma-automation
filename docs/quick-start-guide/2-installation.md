# Installation

The Automation Lab can be installed locally, or ran with a Docker container. Both approaches are described below

## Local installation

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

For additional options, check the install help with:

```shell
./install.sh -h
```

## Docker container

### Get or Build the image

The Automation Lab image should be available as `witekio/automation-lab` directly if you are registered and part of Witekio's team in Docker HUB. Otherwise, you can easily build it:
* Clone the Automation Lab repository
* Navigate to the root and run `make docker-build`, or `make docker-build-arm` on an ARM device. If the build succeeds, you have your Docker image ready.

### Run with make

To run the Automation Lab container using make, you must specify your project directory and the relative path of the script to run within that directory.

* `PROJECT_DIR` - Path to the top level project directory to be mounted in the container
  * Must include all scripts required to run the PROJECT_SCRIPT
  * Can be absolute or relative
* `PROJECT_SCRIPT` - Relative path from within PROJECT_DIR to the script to run

For example:

```shell
make docker-run PROJECT_DIR=/path/to/my/project PROJECT_SCRIPT=myscript.py
```

In order to use SD Wire or USB serial devices you must run the container in privileged mode.
You can do this with `make docker-run-privileged`.

For example:

```shell
make docker-run-privilidged PROJECT_DIR=/path/to/my/project PROJECT_SCRIPT=myscript.py
```

**Warning:** _This will give the container access to all of your system devices. Use with caution._

Running `make-docker-run` without specifying `PROJECT_SCRIPT` will drop you at the terminal prompt within the container.

### Run manually (Not recommended)

When running the Automation Lab container manually, you have to mount the folder containing your Automation Lab test script and run as below:

```shell
  docker run -it --rm -v (pwd):/root witekio/automation-lab python3 /root/my_test_script.py
```

Note: To use the SD Wire of USB Serial adaptors you must invoke docker run with the arguments `--privileged -v /dev:/dev`.

```shell
  docker run -it --rm --privileged -v /dev:/dev -v (pwd):/root witekio/automation-lab python3 /root/my_test_script.py
```

**Warning:** _This will give the container access to all of your system devices. Use with caution._

### Run with GitLab CI pipeline

From your test repository, you can simply use Docker HUB's image (after granting access to the registry), or push the automation lab image in the project's registry.

1. Register your test device as a Docker SSH GitLab runner, with a dedicated tag (e.g. `automation-lab-tester`): https://docs.gitlab.com/runner/
1. Push the Automation Lab Docker image to your project registry: https://docs.gitlab.com/ee/user/packages/container_registry/
1. Create a `.gitlab-ci.yml` file in your repository configured as below

```
device-test-job:
  image: registry.gitlab.com/witekio/<your-project>/automation-lab:latest
  tags:
    - automation-lab-tester         # This should match your GitLab runner tag
  script:
    - python3 my_test_script.py     # Run your automation lab script
```

Now every time your pipeline runs, it will run your test script from your automation lab device, and report the test status.
___

<< Previous: [Introduction](./1-introduction.md) |
Next: [Hardware Overview](./3-hardware_overview.md) >>
