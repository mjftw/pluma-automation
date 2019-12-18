# Witekio Lab Development Style Guide
**UNDER DEVELOPMENT**

- [Witekio Lab Development Style Guide](#witekio-lab-development-style-guide)
  - [Introduction](#introduction)
  - [PEP8 Style Guide](#pep8-style-guide)
  - [General Guidelines](#general-guidelines)
    - [Readability](#readability)
    - [Be Explicit](#be-explicit)
    - [Reusablity](#reusablity)
  - [Specific Guidelines](#specific-guidelines)
    - [Exceptions](#exceptions)

## Introduction
This document will outline the recommended coding style to be followed by developers working on the Witekio Automation Lab.

The main rule you should follow when adding code to the Lab *(and you could argue that this applies to any codebase)* is to try to match the coding style for what is already there.
Your code should blend in with its surroundings, like a stealthy chameleon in a tree.  

To quote [PEP20 - The Zen of Python](https://www.python.org/dev/peps/pep-0020/):

> Beautiful is better than ugly!  
> Explicit is better than implicit!  
> Simple is better than complex!  
> Complex is better than complicated!  
> Flat is better than nested!  
> Sparse is better than dense!  
> Readability counts!  
> Special cases aren't special enough to break the rules!  
> Although practicality beats purity!  
> Errors should never pass silently!  
> Unless explicitly silenced!  
> In the face of ambiguity, refuse the temptation to guess!  
> There should be one-- and preferably only one --obvious way to do it!  
> Although that way may not be obvious at first unless you're Dutch!  
> Now is better than never!  
> Although never is often better than *right* now!  
> If the implementation is hard to explain, it's a bad idea!  
> If the implementation is easy to explain, it may be a good idea!  
> Namespaces are one honking great idea -- let's do more of those!  

As a general guide to write good Python, that works well and is easy to maintain, this works pretty well!

## PEP8 Style Guide
When writing code for the Lab, we try to follow Python's [PEP8](https://www.python.org/dev/peps/pep-0008/) wherever possible.  
The is the de facto community accepted style guide for all new Python code. Follow it and you're bound to end up with reasonably well styled code.

What PEP8 does tell you:
- Where to put your whitespace
- How to layout your code
- How to name your variables, classes, and functions
- ...


What it doesn't tell you:
- How to write readable code
- How to write reusable code
- How to write good code
- ...

E.g.
```python
# Yes:
    spam(ham[1], {eggs: 2})
# No:
    spam( ham[ 1 ], { eggs: 2 } )

# ---------------------------------

# Yes:
    if greeting:
        ...
# No:
    if greeting == True:
        ...
# Worse:
    if greeting is True:
        ...
```

This should be used as a guide; it does not lay down a strict rule that you must follow.  
If you come across a scenario where breaking these rules provides more readable code, then follow your instincts and the guide. You will see a fair few places that PEP8 is not strictly adhered to in the codebase, mostly on line length and indentation rules.  
It's worth noting that you should only ignore the PEP8 guidelines if you have a good reason to.

The easiest way to make sure your code is compliant is to install a linter.  
There are many linters available for this purpose, but I would recommend [Pylama](https://github.com/klen/pylama), as this one is known to work. I use [VS Code ](https://code.visualstudio.com/) for development, and there is an extension available to make this liter run by default. Linters should be available for many other code editors as well.  
Using a linter will help you write better code, with less effort.

All the Lab code uses Python3, make sure your linter is set up for this as it may default to Python2.

## General Guidelines
This section covers some key points to follow to help write good code.  
You could make the argument that these points could help you write better code on any project!

### Readability
Readability is key.  
Write all your code on the assumption that tomorrow you may forget everything about the code you wrote today.  
This assumption forces you to write well documented, easy to read code that another engineer *(or yourself in 6 months!)* could start using and developing with minimal effort.

A good quote from the book [Clean Code](https://www.oreilly.com/library/view/clean-code/9780136083238):
> “Indeed, the ratio of time spent reading versus writing is well over 10 to 1. We are constantly reading old code as part of the effort to write new code. ...[Therefore,] making it easy to read makes it easier to write.”  
-Robert C. Martin, Clean Code: A Handbook of Agile Software Craftsmanship 

This book is currently available to read online for free, and is well worth a look if you have some free time.

### Be Explicit

Just because you can use shorthand for your variable names, it doesn't mean you should.
It is pretty common practice to use shorthand for your imports.  
E.g.
```python
import pandas as pd
import plotly as pl
import pygal as pg

a = pl.xyz
b = pd.xyz
c = pg.xyz
```
While this is a common practice, I would argue that it does not produce readable code; If the reader has to constantly look at your list of imports to know what's going on, your code is not readable enough!

A more readable way to write this would be:
```python
import pandas
import plotly
import pygal

meaningful_name = plotly.xyz
something_explicit = pandas.xyz
aviod_ambiguity = pygal.xyz
```
The same principle applies when picking variable names:
- Well named variables are better than well commented ones.
- Well commented variables are better than nothing.

When passing arguments to functions or class instantiations with more than one or two variables, always use named arguments.  
This ensures that the reader can immediately see what the class is being set up to do, without having to look at the class definition.  
This also means that you do not need to fill in all the default arguments for a class constructor, allowing you to only define the parameters that are needed.
Another benifit of this approach is that it offers some immunity to the order of variables in the class definition changing as the code develops.  
Never rely on the order of your arguments to get correct functionality!

E.g.
```python
# Class definition modified from email.py
# ================================================
class Email():
    """ Create and send emails """
    def __init__(self, sender=None, to=[], cc=[], bcc=[],
            subject=None, body=None, body_type='html'):
        # Class constructor
        ...


# Instantiation in my_code.py
# ================================================

# Bad:
email = Email('foo@gmail.com', 'bar@outlook.com', [], [], 'My Subject', 'Email body', 'html')

# Good
email = Email(
    sender='foo@gmail.com',
    to='bar@outlook.com',
    subject='My Subject',
    body='Email body'
)
```


### Reusablity
When at all possible, code should be written to be as reusable as possible.  
This topic could fill many chapters of a book on it's own, but a few key points could be:
- Avoid dependencies wherever possible
- Make every class and function have just one job that it does well
- Write code to be as generic as possible
- ...

If you are writing something that is not specifically related to the project you are working on, then maybe this code would be a good addition to the `farm-core` core codebase, rather than the repository for the project.  
Adding code to the core codebase (where appropriate) means that the Lab may suddenly gain a new ability, that can be reused on many future projects.

## Specific Guidelines

### Exceptions

We use exceptions to trigger when something has gone wrong, allowing us to never have silent failures.  
To facilite this, exception names should match the problem they are designed to indicate.

E.g.
```python
class MultimeterMeasurementError(MultimeterError):
    pass
```

In the above example you can see that we have defined an new exception class, inheriting from `MultimeterError`. This is our base exception for all multimeter related exceptions, present in `multimeter.py`.

```python
class MultimeterError(Exception):
    pass
```

If you need to add a new exception type for a given set of classes (e.g. Board related exceptions), then you should first add a base class that matches, as shown with `MultimeterError`.

All new exceptions should br prefaced with a word describing the class of exceptions.
```python
# Bad
class MeasurementError(Exception):
    pass

# Good
class MultimeterMeasurementError(MultimeterError):
    pass
```


In order to simplify importing exceptions in external scripts, we have a separate execeptions file (`exceptions.py`).  
When adding new exceptions for a class to use, make sure to add this new exception to the exception file, so that it can be accessed outside of the package, without having to know exactly what file it is actually defined in.

E.g. (Excerpt from `exceptions.py`)
```python
from .board import BoardError, BoardBootValidationError
from .modem import ModemError
```

This allows external scripts to use the exceptions, without having to know the full path to the python file that defines them.  
Not only does this make writing code easier, it also gives some protection against the internal structure of farmcore/farmtest/farmutils changing.

E.g. (External script)
```python
# Without using exceptions.py
from farmcore.baseclasses.consolebase import ConsoleLoginFailedError
from farmcore.board import BoardBootValidationError

# With exceptions.py
from farmcore.exceptions import ConsoleLoginFailedError, BoardBootValidationError
```

The former is vulnerable to breaking if for instance `ConsoleLoginFailedError` moved to a different file in a new version of `farmcore`, but the latter is would not break.