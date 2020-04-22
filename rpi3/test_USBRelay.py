import RPi.GPIO as GPIO
import time

from fixtures import relay_pins, usb_relay

def assert_continuity(output_pin, input_pin, repititions=100):
    # Toggle output and check input matches
    # Repeat many times to rule out floating input matching output by chance
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
