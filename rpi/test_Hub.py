from fixtures import hub, hub_serial_path, hub_relay_path, hub_sdwire_path,\
    hub_ethernet_path


# Serial
def test_Hub_get_serial_finds_device(hub, hub_serial_path):
    devinfo = hub.get_serial()
    assert devinfo


def test_Hub_get_serial_finds_correct_device(hub, hub_serial_path):
    devinfo = hub.get_serial()
    assert devinfo['usbpath'] == hub_serial_path


def test_Hub_get_serial_gets_correct_parameter(hub, hub_serial_path):
    usbpath = hub.get_serial('usbpath')
    assert usbpath == hub_serial_path


# Relay
def test_Hub_get_relay_finds_device(hub, hub_relay_path):
    devinfo = hub.get_relay()
    assert devinfo


def test_Hub_get_relay_finds_correct_device(hub, hub_relay_path):
    devinfo = hub.get_relay()
    assert devinfo['usbpath'] == hub_relay_path


def test_Hub_get_relay_gets_correct_parameter(hub, hub_relay_path):
    usbpath = hub.get_relay('usbpath')
    assert usbpath == hub_relay_path


# SD Wire
def test_Hub_get_sdwire_finds_device(hub, hub_sdwire_path):
    devinfo = hub.get_sdwire()
    assert devinfo


def test_Hub_get_sdwire_finds_correct_device(hub, hub_sdwire_path):
    devinfo = hub.get_sdwire()
    assert devinfo['usbpath'].startswith(hub_sdwire_path)


def test_Hub_get_sdwire_gets_correct_parameter(hub, hub_sdwire_path):
    usbpath = hub.get_sdwire('usbpath')
    assert usbpath.startswith(hub_sdwire_path)


# Ethernet
def test_Hub_get_ethernet_finds_device(hub, hub_ethernet_path):
    devinfo = hub.get_ethernet()
    assert devinfo


def test_Hub_get_ethernet_finds_correct_device(hub, hub_ethernet_path):
    devinfo = hub.get_ethernet()
    assert devinfo['usbpath'] == hub_ethernet_path


def test_Hub_get_ethernet_gets_correct_parameter(hub, hub_ethernet_path):
    usbpath = hub.get_ethernet('usbpath')
    assert usbpath == hub_ethernet_path
