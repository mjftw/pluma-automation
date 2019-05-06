import time

from serial import Serial


class MultimeterError(Exception):
    pass


class MultimeterInvalidKeyPress(MultimeterError):
    pass


class MultimeterMeasurementError(MultimeterError):
    pass


class MultimeterDecodeError(MultimeterError):
    pass


class MultimeterTTI1604():
    button_map = {
        'Up':        b'a',
        'Down':      b'b',
        'Auto':      b'c',
        'A':         b'd',
        'mA':        b'e',
        'V':         b'f',
        'Operate':   b'g',
        'Ohm':       b'i',
        'Hz':        b'j',
        'Shift':     b'k',
        'AC':        b'l',
        'DC':        b'm',
        'mV':        b'n',
        'remote_mode': b'u',
        'local_mode':  b'v'
    }

    char_map = {
        252: '0',
        96:  '1',
        218: '2',
        242: '3',
        102: '4',
        182: '5',
        190: '6',
        224: '7',
        254: '8',
        230: '9',
        238: 'A',
        156: 'C',
        122: 'D',
        158: 'E',
        142: 'F',
        140: 'R',
        30:  'T',
        124: 'U',
        28:  'L',
        0:   '',
        2:   ''
    }

    unit_bitfield_map = {
        1: 'mV',
        2: 'V',
        3: 'mA',
        4: 'A',
        5: 'ohm',
        6: 'Continuity',
        7: 'Diode Test'
    }

    def __init__(self, port):
        self.serial = Serial(baudrate=9600, timeout=0.5, port=port)

        # We need +9V on DTR to power opto-isolation in TTI1604
        self.serial.setDTR(1)
        # We need -9V on RTS to power opto-isolation in TTI1604
        self.serial.setRTS(0)
        self.press_button('remote_mode')

        self.last_unit = None

    @property
    def is_ready(self):
        # If we are recieving data, it's on, otherwise it's off.
        self.serial.flushInput()

        return True if (self.serial.read() != b'') else False

    def press_button(self, button):
        try:
            self.serial.write(self.button_map[button])
        except KeyError:
            raise MultimeterInvalidKeyPress(
                'Multimeter does not have button "{}"'.format(button))

    def power_on(self):
        if not self.is_ready:
            self.press_button('Operate')
            self.press_button('remote_mode')

    def measure(self, unit):
        valid_units = ['mV', 'V', 'mA', 'A', 'ohm']

        unit = unit.lower()
        if unit not in [u.lower() for u in valid_units]:
            raise RuntimeError('Unit must in list {}'.format(valid_units))

        if self.last_unit and self.last_unit.lower() != unit:
            self.set_unit(unit)

        decoded_data, decoded_unit = self._sample_and_decode()

        if decoded_unit.lower() != unit:
            self.set_unit(unit)
            decoded_data, decoded_unit = self._sample_and_decode()

        self.last_unit = decoded_unit

        return decoded_data

    def set_unit(self, unit):
        if unit == 'v':
            self.press_button('V')
        elif unit == 'mv':
            self.press_button('mV')
        elif unit == 'a':
            self.press_button('A')
        elif unit == 'ma':
            self.press_button('mA')
        elif unit == 'ohm':
            self.press_button('Ohm')
        else:
            raise NotImplementedError

        # Give multimeter time to settle
        time.sleep(1)

    def _sample_and_decode(self):
        max_attempts = 3
        for num_bad_rx in range(1, max_attempts):
            try:
                data = self._get_sample()
                decoded_data, decoded_unit = self._decode_data(data)
                break
            except MultimeterDecodeError as e:
                if num_bad_rx >= max_attempts:
                    raise e

        return decoded_data, decoded_unit

    def _get_sample(self):
        packet = []
        packet_len = 10
        bytes_read = 0

        self.serial.flushInput()

        # Find alignment of next packet
        while(self.serial.read() != b'\r' and bytes_read <= packet_len):
            bytes_read += 1

        if bytes_read >= packet_len:
            raise MultimeterMeasurementError(
                'Could not get a valid response from multimeter')

        for _ in range(1, packet_len):
            packet.append(
                int.from_bytes(self.serial.read(), byteorder='little'))

        return packet

    def _decode_data(self, data):
        if not isinstance(data, list) or len(data) < 9:
            raise MultimeterDecodeError('Invalid data')

        range_info = '{:08b}'.format(data[0])
        # func_info = '{:08b}'.format(data[1]) # Igonored for now
        sign_info = '{:08b}'.format(data[2])
        digits_info = data[3:8]

        unit = self.unit_bitfield_map[_bitfield_int(range_info, 0, 2)]
        # acdc = 'AC' if _bitfield_int(range_info, 3, 3) else 'DC'  # Igonored for now
        sign = '-' if _bitfield_int(sign_info, 1, 1) else '+'

        digits = []
        decimal_place = None
        for di in digits_info:
            digit = None
            for i in range(0, 2):
                try:
                    digit = self.char_map[di-i]
                    decimal_place = i
                    break
                except KeyError:
                    pass

            if digit is None:
                raise MultimeterDecodeError('Unable to decode digit [{}]'.format(di))

            digits.append(digit)
            if decimal_place > 0:
                digits.append('.')
        value = ''.join(digits)

        if '0FL' in value or '0.FL' in value or '0F.L' in value:
            data_str = 'overflow'
        else:
            data_str = '{}{}'.format(sign, value)

        if len(data_str) <= 2:
            raise MultimeterDecodeError('Invalid data')

        return data_str, unit

def _bitfield_int(byte_str, start_bit, stop_bit):
    return int(byte_str[7-stop_bit:8-start_bit], 2)