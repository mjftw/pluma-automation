from fixtures import hub, usb_serial_path


def test_Hub_get_serial_finds_device(hub, usb_serial_path):
    devinfo = hub.get_serial()
    assert devinfo


def test_Hub_get_serial_finds_correct_device(hub, usb_serial_path):
    devinfo = hub.get_serial()
    assert devinfo['usbpath'] == usb_serial_path
