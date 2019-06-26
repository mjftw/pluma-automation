# Automation Lab Quick Start Guide
**===== IN DEVELOPMENT =====**

This guide will aim to give an introduction to the layout of the codebase, and the minimum steps that must be followed in order to start using it.

## Repositories
The Automation Lab is designed in such a way that the core code is able to remain separate from project specific tests, setup etc.

In order to facilitate this, any code that could be reused in any project is found in the repository named [farm-core][farm-core].

For customer specific modifications, a second reposiory should be created, following the naming format "farm-\<customer>".
An example of this is [farm-plexus][farm-plexus].

You will likely create one such repository for your project, using it as your working directory, and including content from farm-core in order to control hardware, run tests, and more.
Expect to modify your "farm-\<customer>" repisitory frequently, whilst leaving [farm-core][farm-core] unchanged unless really needed.

## Core Codebase (farm-core)
The basic structure of [farm-core][farm-core] is shown below:
```
.
├── farmcore            - Hardware control classes
│   ├── ...
│   └── baseclasses     - Bases for types of class
│       └── ...
├── farmtest            - Testing framwork
│   ├── ...
│   └── stock           - Generic tests and fucntions that apply to any project
│       └── ...
├── farmutils           - Utility functions
│   └── ...
├── docs                - Documentation
│   └── ...
├── install_deps.sh     - Dependencies installation script
└── ...
```


[farm-core]: https://bitbucket.org/adeneo-embedded/farm-core
[farm-plexus]: https://bitbucket.org/adeneo-embedded/farm-plexus

## Environment Setup

1. Clone farm-core
1. Clone farm-\<your project here\>
1. Add the following to your `.bashrc` file:
    ```
    export LAB_INSTALL_DIR="/full/path/to/farm-core"
    ```
1. Logout and login or run:
    ```
    source ~/.bashrc
    ```
