# Farm Core **[QSG: TO GO IN FARM SOFTWARE OVERVIEW]**

This code is designed to drive the farm in 2018 where we have the components

1. SDMUX
2. USB Relay
3. APC network device
4. USB Serial

# Usage

## Structure **[QSG: TO GO IN FARM SOFTWARE OVERVIEW]**

The project for working with farm code should be split up as follows - 

1. "/farmcore" directory for the farm-core code ( in this repo )
2. "/farmconfigs" directory for the farm-config code ( in this repo )
3. Your source code ( which should import a config from "farmconfigs" )


## Farm Configs **[QSG: TO GO IN TUTORIAL 1]**

Farm impimentations need to be mapped out in software with a farm config file. This is then stored
in this repo and used centrally by mulitple users. It should always mirror the hardware layout of the farm
and modifications should be broadcast to other users in case there are conflicts.

An example farm config for the UK farm is as follows:

```python
from farmcore import farm

apc1 = farm.APC('10.103.3.40', 'apc','apc')

ur1 = farm.USBRelay( '1-1.1.4.1')
ur2 = farm.USBRelay( '1-1.1.4.3')

sdm1 = farm.SDMux( ur2[0], apc1[2])
sdm2 = farm.SDMux( ur2[3], apc1[1])
sdm3 = farm.SDMux( ur2[2], apc1[3])

bbb = farm.Board('bbb', apc1[7], '1-1.1.1', sdm1)
fb42 = farm.Board('fb42', apc1[4], '1-1.1.2', sdm2)
fb43 = farm.Board('fb43', apc1[6], '1-1.1.3', sdm3)
```

The above represents the hardware layout of the farm in the UK office. This file should then 
be included in all scripts which wish to interact with the farm.

## Setup references **[QSG: TO GO IN TUTORIAL 2]**

The farm-core source is NOT packaged up and isn't intended to be installed as a system package. 
Therefore we must add its location to the PYTHONPATH variable so that the python interpreter can pick it up.

The simplest way of doing this is adding the following at the top of the script:

```python
import sys
sys.path.append('/home/wsheppard/farm-core')
```

alternatively you can set the environment variable:

```bash
export PYTHONPATH=/home/wsheppard/farm-core
```

## Example Use **[QSG: TO GO IN TUTORIAL 2]**

The following is a very simple guide to turn on a board using the farm_uk config as shown above:

```python
# Setup references
import sys
sys.path.append('/home/wsheppard/farm-core')

# This imports the board definitions and also gives us a farm handle
# Remember - replace "farm_uk" here with your hardware description filename
from farmconfigs.farm_uk import farm

# Get a handle to the simple board class for the board named "fb42" ( see above )
b = farm.get_board( 'fb42' )

# Issue a use request on this which returns our FarmBoard class with which we can perform all
# the farm actions.
fb = b.use()

# Turn on the board
fb.on()

# Turn off the board
fb.off()

# Please see the ( as yet unwritten ! ) API Docs for further info
```


# Installation **[QSG: TO GO IN INSTALLATION SECTION]**

Checkout this repo into a directory you can access and reference.

In your source directory ( recommeneded to be different from this repo ) you create your hardware
description file ( mentioned above )
And also your source files for using the farm.



