# Automation Lab Design Core Values

This document describes the core values that should be kept in mind when adding new code and feature to the Automation Lab.

## Language
All core code should be written in Python3.

Advantages of fully Python codebase:  
- Python is a well used modern language which is easy to learn  
- Python runs almost everywhere these days, offering great portability  
- A Python project is easy to set up, with no compilation required  
- Development is faster, more efficient and flexible when no the same code can be run on the development machine and target hardware without modification or compilation  
- A fully Python codebase means that all classes may be used in an interactive manner via the interactive Python interperator, giving a command line interface for free  
- The entire project can be easily debugged using the Python debugger  
  - Having parts of the core functionality written in a different language would break the debugger's ability to fully trace the source tree  

## Self contained

Wherever possible the codebase should be fully self contained.

This means avoiding dependancy on external services such as Jenkins, or SQL database servers unless strictly neccesary.  
Python is a pretty mature language, with packages to do just about anything. There is likely another way to do something without the need for an external service or server.  
Keeping the codebase self contained reduces project dependancies, and greatly reduces the work required to run a lab instance as you do not have to worry about having servers _X_, _Y_, and _Z_ up before runtime.

## Ease of use

The codebase should be easy to set up and use.

Setting up a machine to run the lab code should be as easy as runinng a script.  
This script will install all required packages via the Python Package Index [pip](https://pypi.org/project/pip/). Where this is not possible, packages can be installed via the Ubuntu package manager.

## Modular

The code base should be written in such a way that it remains modular.

This means reducing the coupling between different parts of the codebase, allowing each class to be usable without dependancy on any other.  
This way a user only needs import the project elements that they actually want to use, keeping code simple and readable.  
Classes with low coupling are also easy to use in an interactive Python session, giving the lab a command line interface for free.