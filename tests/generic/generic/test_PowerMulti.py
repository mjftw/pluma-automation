from pluma.core import PowerMulti
from pluma.core.baseclasses import PowerBase


class MockPower(PowerBase):
    def __init__(self, mocks_on_list=None, mocks_off_list=None):
        PowerBase.__init__(self, reboot_delay=0)

        self.mocks_on_list = mocks_on_list if mocks_on_list is not None else []
        self.mocks_off_list = mocks_off_list if mocks_off_list is not None else []
        self.on_called = 0
        self.off_called = 0

    @PowerBase.on
    def on(self):
        self.on_called += 1
        self.mocks_on_list.append(self)

    @PowerBase.off
    def off(self):
        self.off_called += 1
        self.mocks_off_list.append(self)


def test_PowerMulti_calls_targets_on_methods():
    num_mock_powers = 3
    mock_powers = [MockPower() for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers
    )

    power.on()

    assert(all([mp.on_called == 1 for mp in mock_powers]))


def test_PowerMulti_calls_targets_on_methods_in_correct_order():
    mocks_on_list = []
    num_mock_powers = 3
    mock_powers = [MockPower(mocks_on_list=mocks_on_list)
                   for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers
    )

    power.on()

    assert(mock_powers == mocks_on_list)


def test_PowerMulti_calls_targets_off_methods():
    num_mock_powers = 3
    mock_powers = [MockPower() for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers
    )

    power.off()

    assert(all([mp.off_called == 1 for mp in mock_powers]))


def test_PowerMulti_calls_targets_off_methods_in_sequence_order_with_reverse_off_seq_false():
    mocks_off_list = []
    num_mock_powers = 3
    mock_powers = [MockPower(mocks_off_list=mocks_off_list)
                   for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers,
        reverse_off_seq=False
    )

    power.off()

    assert(mock_powers == mocks_off_list)


def test_PowerMulti_calls_targets_off_methods_in_reverse_order_with_reverse_off_seq_true():
    mocks_off_list = []
    num_mock_powers = 3
    mock_powers = [MockPower(mocks_off_list=mocks_off_list)
                   for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers,
        reverse_off_seq=True
    )

    power.off()

    assert(mock_powers[::-1] == mocks_off_list)


def test_PowerMulti_calls_targets_off_methods_in_reverse_order_with_reverse_off_seq_default():
    mocks_off_list = []
    num_mock_powers = 3
    mock_powers = [MockPower(mocks_off_list=mocks_off_list)
                   for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers
    )

    power.off()

    assert(mock_powers[::-1] == mocks_off_list)


def test_PowerMulti_calls_targets_reboot_methods():
    num_mock_powers = 3
    mock_powers = [MockPower() for __ in range(0, num_mock_powers)]

    power = PowerMulti(
        power_seq=mock_powers
    )

    power.reboot()

    assert(all([mp.on_called == 1 and mp.off_called == 1 for mp in mock_powers]))
