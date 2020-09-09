''' pluma.core.USBRelay class tests

These tests require that the USB Relay (DLP-IOR4) be set up in a certain way.
Four GPIOs on the RPi must also be connected to the USB Relay.
The RPi pins used for this should be set in the config file "hardware.json".

The USB path for the USB Relay must also be in "hardware.json".
This can be found in Linux by running "dmesg -w", then plugging in the USB
relay.

The output should look like:
[ 7570.491865] usb 1-1.2: Product: DLP-IOR4
[ 7570.491877] usb 1-1.2: Manufacturer: DLP Design

In this case the USB path is "1-1.2".
This path will change depending on what USB port/ USB hub port the USB device
is connected to.

The USB Relay should be set up with wires connecting the terminal blocks
and RPi GPIOs as shown below:

### Connections for A ports ###
RPi_GPIO -> 1_A
1_common -> 2_A
2_common -> 3_A
3_common -> 4_A
4_common -> RPi_GPIO

When all switches are set to port A, a connection is made between the
output GPIO on 1_A and the input GPIO on 4_common

### Connections for B ports ###
RPi_GPIO -> 1_common
1_B      -> 2_common
2_B      -> 3_common
3_B      -> 4_common
4_B      -> RPi_GPIO

When all switches are set to port A, a connection is made between the
output GPIO on 1_common and the input GPIO on 4_B.
'''

import RPi.GPIO as GPIO
import time

from fixtures import relay_pins, usb_relay


def assert_continuity(output_pin, input_pin, repititions=100):
    ''' Toggle output and check input matches to assert continuity
    Repeat many times to rule out floating input matching output by chance
    '''

    for __ in range(0, repititions):
        GPIO.output(output_pin, GPIO.HIGH)
        time.sleep(0.001)
        assert GPIO.input(input_pin) == GPIO.HIGH

        GPIO.output(output_pin, GPIO.LOW)
        time.sleep(0.001)
        assert GPIO.input(input_pin) == GPIO.LOW


def setup_gpios(inputs, outputs):
    GPIO.setmode(GPIO.BOARD)
    for i in inputs:
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
    for o in outputs:
        GPIO.setup(o, GPIO.OUT)


def test_set_switches_to_a(relay_pins, usb_relay):
    setup_gpios(
        inputs=[
            relay_pins['4']['B'],
            relay_pins['4']['Common'],
            relay_pins['1']['Common']
        ],
        outputs=[
            relay_pins['1']['A']
        ]
    )

    for port in [1, 2, 3, 4]:
        usb_relay.toggle(port, 'A')

    # Wait for relays to move
    time.sleep(0.1)

    # If all pins switch correctly, 1-A should connect to 4-Common
    assert_continuity(relay_pins['1']['A'], relay_pins['4']['Common'])

    # End test with all GPIOs set to inputs for saftey
    setup_gpios(outputs=[], inputs=[relay_pins['4']['B']])


def test_set_switches_to_b(relay_pins, usb_relay):
    setup_gpios(
        inputs=[
            relay_pins['1']['A'],
            relay_pins['1']['Common'],
            relay_pins['4']['Common']
        ],
        outputs=[
            relay_pins['4']['B']
        ]
    )

    for port in [1, 2, 3, 4]:
        usb_relay.toggle(port, 'B')

    # Wait for relays to move
    time.sleep(0.1)

    # If all pins switch correctly, 4-B should connect to 1-Common
    assert_continuity(relay_pins['4']['B'], relay_pins['1']['Common'])

    # End test with all GPIOs set to inputs for safety
    setup_gpios(outputs=[], inputs=[relay_pins['4']['B']])
