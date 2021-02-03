from unittest.mock import patch


def test_SoftPower_on_calls_console_send_with_correct_cmd(soft_power):
    cmd = 'myon'
    soft_power.on_cmd = cmd
    soft_power.on()
    soft_power.console.send.assert_called_with(cmd)


def test_SoftPower_off_calls_console_send_with_correct_cmd(soft_power):
    cmd = 'myoff'
    soft_power.off_cmd = 'myoff'
    soft_power.off()
    soft_power.console.send.assert_called_with(cmd)


def test_SoftPower_reboot_calls_console_send_with_correct_cmd(soft_power):
    cmd = 'myreboot'
    soft_power.reboot_cmd = cmd
    soft_power.reboot()
    soft_power.console.send.assert_called_with(cmd)


@patch('pluma.core.baseclasses.PowerBase.reboot')
def test_SoftPower_reboot_calls_reboot_if_no_reboot_command(mock_base_reboot,
                                                            soft_power):
    soft_power.reboot_cmd = None
    soft_power.reboot()
    mock_base_reboot.assert_called_once()
