from fixtures import hub, hub_usb_serial_path, hub_usb_relay_path


# Serial
def test_Hub_get_serial_finds_device(hub, hub_usb_serial_path):
    devinfo = hub.get_serial()
    assert devinfo


def test_Hub_get_serial_finds_correct_device(hub, hub_usb_serial_path):
    devinfo = hub.get_serial()
    assert devinfo['usbpath'] == hub_usb_serial_path


def test_Hub_get_serial_gets_correct_parameter(hub, hub_usb_serial_path):
    usbpath = hub.get_serial('usbpath')
    assert usbpath == hub_usb_serial_path


# Relay
def test_Hub_get_relay_finds_device(hub, hub_usb_relay_path):
    devinfo = hub.get_relay()
    assert devinfo


def test_Hub_get_relay_finds_correct_device(hub, hub_usb_relay_path):
    devinfo = hub.get_relay()
    assert devinfo['usbpath'] == hub_usb_relay_path


def test_Hub_get_relay_gets_correct_parameter(hub, hub_usb_relay_path):
    usbpath = hub.get_relay('usbpath')
    assert usbpath == hub_usb_relay_path
