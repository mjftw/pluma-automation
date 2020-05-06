# Automation Lab Quick Start Guide

**===== IN DEVELOPMENT =====**

This guide will aim to give an introduction to the layout of the codebase, and the minimum steps that must be followed in order to start using it.

## Repositories

The Automation Lab is designed in such a way that the core code is able to remain separate from project specific tests, setup etc.

In order to facilitate this, any code that could be reused in any project is found in the repository named [farm-core][farm-core].

For customer specific modifications, a second repository should be created, following the naming format "farm-\<customer>".

You will likely create one such repository for your project, using it as your working directory, and including content from farm-core in order to control hardware, run tests, and more.
Expect to modify your "farm-\<customer>" repository frequently, whilst leaving [farm-core][farm-core] unchanged unless really needed.

## Examples and automated tests (farm-example)

Some example test scripts can be found in the [farm-example](farm-example) repository.
This repository also contains all of the automated tests that check that the lab code is still functioning, although these are currently in development.

## Documentation (farm-documentation)

While all of the documentation for the project is found in this repository, it is spread throughout the code in the form of Python docstrings.
There are a number of documents in the `docs` directory as well (including this one).

The [farm-documentation](farm-documentation) does not provide any information that cannot be found in this repository, but it does format it in a much more human readable manner.  
The documentation is built using [Sphinx](sphinx), and is presented as a [Read The Docs](readthedocs) style web page.  
This includes converting all docstrings into an API guide, as well as converting all of the markdown docs you find here.

The [farm-documentation](farm-documentation) repository also contains all the makefiles and scripts required to run a documentation server to host these documents.

## Core codebase (farm-core)

Since quick start guide guide is primarily aimed at getting up and running using the code in this repository, the rest of this guide will focus on the core codebase; [farm-core](farm-core).

The basic structure of [farm-core][farm-core] is shown below:

```
.
├── farmcore            - Hardware control classes
│   ├── ...
│   └── baseclasses     - Bases for types of class
│       └── ...
├── farmtest            - Testing framework
│   ├── ...
│   └── stock           - Generic tests and functions that apply to any project
│       └── ...
├── farmutils           - Utility functions
│   └── ...
├── docs                - Documentation
│   └── ...
├── install.sh          - Installation script
└── ...
```

[sphinx]: https://www.sphinx-doc.org
[readthedocs]: https://readthedocs.org
[farm-documentation]: https://bitbucket.org/adeneo-embedded/farm-documentation
[farm-core]: https://bitbucket.org/adeneo-embedded/farm-core
[farm-example]: https://bitbucket.org/adeneo-embedded/farm-example