# Pluma Automation Quick Start Guide

## Introduction

Pluma Automation is a tool designed to perform black box testing of embedded hardware; designed to be as lightweight as possible!

At it's core it enables programmatic hardware control of many supported devices to control a board's power, console, storage, and more.
This package is named `farmcore`.

On top of the hardware control library sits a testing framework `farmtest`, which automates the hardware control to run testing of many flavours (regression, soak, feature, etc). This package is entirely optional.
`farmcore` still works well without it, and can be easily integrated with other testing frameworks and CI/CD tools such as [Pytest](https://docs.pytest.org/) or [Buildbot](https://buildbot.net/).

Finally we have `farmutils`, a utilities library to provide additional features such as email reporting or downloading code from `git` repositories.

![System Diagram](automation_lab_system_diagram.png)

This guide will aim to give an introduction to the layout of the codebase, and the minimum steps that must be followed in order to start using it.

### Repositories

Pluma Automation is designed in such a way that the core code is able to remain separate from project specific tests, setup etc.

In order to facilitate this, any code that could be reused in any project is found in the repository named [pluma][pluma].

For customer specific modifications, a second repository should be created, following the naming format `farm-<customer>`.

You will likely create one such repository for your project, using it as your working directory, and including content from pluma in order to control hardware, run tests, and more.
Expect to modify your `farm-<customer>` repository frequently, whilst leaving [pluma][pluma] unchanged unless really needed.

### Examples and automated tests (farm-example)

Some example test scripts can be found in the [farm-example][farm-example] repository.
This repository also contains all of the automated tests that check that Pluma code is still functioning, although these are currently in development.

### Documentation (farm-documentation)

All documentation on the `pluma` API can be found alongside the code in the form of docstrings.
This information is useful for finding the specifics of how to use a given class or function, but does not provide any high level information about when they should be used.  
High level documentation can be found `docs` directory, and is focused on describing the intended use cases for various classes and frameworks in the `pluma` library.

The [farm-documentation][farm-documentation] does not provide any information that cannot be found in this repository, but it does format it in a much more human readable manner.  
The documentation is built using [Sphinx][sphinx], and is presented as a [Read The Docs][readthedocs] style web page.  
This includes converting all docstrings into an API guide, as well as converting all of the markdown docs you find here.

The [farm-documentation][farm-documentation] repository also contains all the makefiles and scripts required to run a documentation server to host these documents.

### Core codebase (pluma)

Since quick start guide guide is primarily aimed at getting up and running using the code in this repository, the rest of this guide will focus on the core codebase - [pluma](pluma).

The basic structure of [pluma][pluma] is shown below:

```preformatted-text
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

___

Next: [Install and Run](./2-install-and-run.md) >>

[sphinx]: https://www.sphinx-doc.org
[readthedocs]: https://readthedocs.org
[farm-documentation]: https://bitbucket.org/adeneo-embedded/farm-documentation
[pluma]: https://bitbucket.org/adeneo-embedded/pluma
[farm-example]: https://bitbucket.org/adeneo-embedded/farm-example
