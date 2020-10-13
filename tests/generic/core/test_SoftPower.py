def test_SoftPower_on_calls_console_send(soft_power):
    soft_power.on()

    soft_power.console.send.assert_called()


def test_SoftPower_on_calls_console_send_with_correct_cmd(soft_power):
    soft_power.on()

    soft_power.console.send.assert_called_with(soft_power.on_cmd)


def test_SoftPower_off_calls_console_send_with_correct_cmd(soft_power):
    soft_power.off()

    soft_power.console.send.assert_called_with(soft_power.off_cmd)


def test_SoftPower_off_calls_console_send(soft_power):
    soft_power.off()

    soft_power.console.send.assert_called()
