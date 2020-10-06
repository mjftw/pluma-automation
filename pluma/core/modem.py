import time
import re
import sys

try:
    # The hardware reset functionality requires the use of
    # GPIO. If the test suite is running on a Raspberry Pi,
    # import the GPIO library to enable the feature,
    # else skip the import - this is checked by the
    # 'hardware_reset' method.
    with open('/sys/firmware/devicetree/base/model') as model:
        if 'Raspberry Pi' in model.read():
            import RPi.GPIO as GPIO
except (OSError, IOError):
    pass

from .serialconsole import SerialConsole
from .baseclasses import HardwareBase


class ModemError(Exception):
    pass


class ModemSim868(HardwareBase):
    ''' Diver for the Sim868 based GSM/GNSM/GPS/Bluetooth modem '''

    def __init__(self, port):
        ''' @port: Port of the serial console for sending AT commands '''
        self.console = SerialConsole(port, 115200)

        self._recording_lock = False
        self._recording_paused = False

        self._recording_settings = None
        self._recording_buffer = None

        self.hardware_reset_pin = 7
        self.hardware_reset_wait_period = 4
        self.hardware_reset_max_attempts = 6

    def AT_send(self, *args, **kwargs):
        if self._recording_lock:
            self.error('Cannot send AT commands while recording in progress',
                       ModemError)

        return self.console.send_and_expect(*args, **kwargs)

    def ready(self):
        # Check modem status
        __, matched = self.AT_send('AT', match='OK')
        if not matched:
            return False

        # Check sim ready
        __, matched = self.AT_send('AT+CPIN?', match=r'\+CPIN: READY')
        if not matched:
            return False

        return True

    def phone_activity_status(self, check_while_recording=False):
        '''
        Return phone activity status.
            0: Ready
            2: Unknown
            3: Incoming call
            4: Ongoing call
        '''
        paused_to_check = False
        if self.call_recording_ongoing():
            if check_while_recording:
                self.call_recording_pause()
                paused_to_check = True
            else:
                self.error('Must set check_while_recording to check phone status while recording',
                           ModemError)
        else:
            # Don't check modem is ready if it is already recording
            if not self.ready():
                self.hardware_reset()

        __, matched = self.AT_send('AT+CPAS', match='CPAS: [0-9]+')
        if not matched:
            self.error('Incorrect response from modem', ModemError)

        if paused_to_check:
            self.call_recording_resume()

        substr = re.findall('[0-9]+', matched)
        if not substr or len(substr) == 0:
            raise RuntimeError('Invalid regex match')

        return substr[0]

    def ongoing_call(self, check_while_recording=False):
        ''' If call ongoing, return True, else return False'''
        if self.phone_activity_status(check_while_recording) == '4':
            return True
        else:
            return False

    def incoming_call(self, check_while_recording=False):
        ''' If call incoming, return True, else return False'''
        if self.phone_activity_status(check_while_recording) == '3':
            return True
        else:
            return False

    def answer_call(self, timeout=30, record=False):
        '''
        Expect a call within the next @timeout seconds, and answer when
        it comes through. If record the call if @record is set.
        If there is an ongoing call, it is ended.
        Returns None if no call received in @timeout seconds.
        Returns phone number of caller if call received
        '''
        if self.ongoing_call():
            self.log('Ending ongoing call')
            self.end_call()

        if not self.ready():
            self.hardware_reset()

        # Enable call notification and wait for incoming
        received, matched = self.AT_send(
            cmd='AT+CLIP=1', match=r'\+CLIP: "\+{0,1}[0-9]+"', timeout=timeout)
        if not matched:
            return None

        substr = re.findall(r'\+{0,1}[0-9]+', matched)
        if not substr or len(substr) == 0:
            raise RuntimeError('Invalid regex match')
        caller = substr[0]

        self.log('Answering incoming call from {}'.format(caller))

        # Answer call
        received, matched = self.AT_send('ATA', match='OK')

        if record:
            raise NotImplementedError

        return caller

    def end_call(self):
        '''
        End an ongoing call
        '''
        if not self.ongoing_call():
            self.log('No call ongoing')
            return False

        __, matched = self.AT_send('ATH', match='OK')
        if not matched:
            self.error('Could not end call', ModemError)

        self.log('Call ended')
        return True

    def make_call(self, number):
        '''
        Start a phone call to the number @number.
        Returns true if call connected, False otherwise.
        If a call is already ongoing, False is returned.
        '''

        if not self.ready():
            self.hardware_reset()

        if self.ongoing_call():
            self.log('Cannot make call, call ongoing')
            return False

        self.log('Calling {}'.format(number))

        received, matched = self.AT_send('ATD{};'.format(number),
                                         match=['OK', 'NO DIALTONE', 'BUSY',
                                                'NO CARRIER', 'NO ANSWER'],
                                         excepts='ERROR')
        if not matched:
            self.error(f'Unexpected response from modem: {received}', ModemError)

        if matched == 'OK':
            if not self.ongoing_call():
                self.error('Call connected, but not ongoing', ModemError)
            self.log('Call connected')
            return True
        elif matched == 'NO DIALTONE':
            self.log('Call not connected, no dial tone')
        elif matched == 'BUSY':
            self.log('Call not connected, line busy')
        elif matched == 'NO CARRIER':
            self.log('Call not connected, no carrier')
        elif matched == 'NO ANSWER':
            self.log('Call not connected, no answer')

        return False

    def call_recording_ongoing(self):
        '''
        Returns True if call recording in progress
        '''
        return self._recording_lock

    def call_recording_start(self):
        '''
        Start a call recording.
        Starting a recording causes modem to stream audio data over UART.
        Starting recording stops AT commands from being sent until recording stops.
        Starting a recording drops any data buffered from paused recordings.
        '''
        if self.call_recording_ongoing():
            self.log('Cannot start recording, recording in progress')
            return False

        if self._recording_paused:
            self.log('Discarding paused recording data')

        # Clear any saved data from paused recordings
        self._recording_buffer = None

        # Start a recording, with data sent at a 100ms interval,
        # and a no sent at the end of transmission.
        # __, matched = self.AT_send('AT+CRECORD=1,5,2', #last 2 bytes are crc

        self._recording_settings = '1,5,0'
        self._start_recoding()

        self.log(
            'Started recording. Do not try to send AT commands before ending recording')

        return True

    def call_recording_stop(self, file):
        '''
        Stop an ongoing call recording or paused recording.
        Returns True if recording saved to @file.
        Returns False if no recording is ongoing.
        Output file format is AMR 4.75k.
        '''
        if not self.call_recording_ongoing() and not self._recording_paused:
            self.error('No ongoing or paused recording, cannot stop',
                       ModemError)
            return False

        self._stop_recoding_and_buffer()

        with open(file, 'wb') as f:
            # Write AMR file header
            f.write(b'#*AMR\n')
            f.write(self._recording_buffer)

        self._recording_buffer = None
        self._recording_lock = False
        self._recording_paused = False

        self.log('Call recording stopped')

        return True

    def call_recording_pause(self):
        '''
        Pause an ongoing recording, saving data to an internal buffer.
        Pausing recording allows other AT commands to be sent.
        Returns True if an ongoing recording was paused, False otherwise
        '''
        if self._recording_paused:
            self.log('Recording already paused')
            return False

        if not self.call_recording_ongoing():
            self.log('No call recording ongoing, no need to pause')
            return False

        self.log('Pausing call recording...')

        self._stop_recoding_and_buffer()

        self._recording_lock = False
        self._recording_paused = True

        return True

    def call_recording_resume(self):
        '''
        Resume a paused recording, restoring saved data from the buffer
        Return True if recording resumed, False if no recording ongoing
        '''
        if self.call_recording_ongoing():
            self.log('Call recording ongoing, no need to resume')
            return False

        if not self._recording_paused:
            self.error('No paused recording to resume', ModemError)

        self._start_recoding()

        self.log('Call recording resumed')

        return True

    def _stop_recoding_and_buffer(self):
        serial = self.console._ser

        # Write any data to serial to stop recording
        serial.write(self.console.encode('0'))

        data = serial.readall()

        # Strip out AT commands from start and end of data
        if data.startswith(self.console.encode('\r\n+CRECORD:')):
            data = data[len('\r\n+CRECORD:'):]
        if data.endswith(self.console.encode('\r\nOK\r\n')):
            data = data[:-len('\r\nOK\r\n')]

        if self._recording_buffer:
            self._recording_buffer += data
        else:
            self._recording_buffer = data

    def _start_recoding(self):
        __, matched = self.AT_send('AT+CRECORD={}'.format(self._recording_settings),
                                   match=['OK', 'CRECORD'], excepts='ERROR')
        if not matched:
            self.error('Failed to start recording', ModemError)

        # Flush serial input buffer
        self.console.read_all()

        # From this point, directly interact with Serial Object
        self._recording_lock = True
        self._recording_paused = False

    def send_sms(self, number, message):
        '''Send the SMS message @message to @number'''
        if not self.ready():
            self.hardware_reset()

        # Set SMS to text mode
        __, matched = self.AT_send('AT+CMGF=1', match='OK')
        if not matched:
            self.error('Failed to set SMS mode to text', ModemError)

        # Start writing text
        __, matched = self.AT_send('AT+CMGS="{}"'.format(number), match='>')
        if not matched:
            self.error('SMS start command failed', ModemError)
        __, matched = self.AT_send('{}\x1A'.format(message),
                                   match='CMGS', timeout=20)
        if not matched:
            self.error('Failed to send SMS', ModemError)

        self.log('SMS sent')

    def read_sms(self, sms_number=None):
        '''
        Returns a list of all SMS messages received if @sms_number
        is None, else returns only SMS at @sms_number.
        Returns None if SMS at @sms_number does not exist.
        '''
        raise NotImplementedError

    def delete_sms(self, sms_number=None):
        '''
        Deletes the sms at @sms_number if it exists.
        If @sms_number is None, deletes all SMS.
        Returns True if delete successfull, or False if not
        '''
        raise NotImplementedError

    def sms_received(self):
        '''Returns the number of SMS received'''
        raise NotImplementedError

    def hardware_reset(self):
        # Check if the Raspberry Pi GPIO library is loaded
        if 'RPi.GPIO' in sys.modules:
            reset_successful = False
            # Setup reset pin in output mode
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.hardware_reset_pin, GPIO.OUT)
            for i in range(self.hardware_reset_max_attempts):
                # Toggle the GPIO until the modem is responsive to AT commands,
                # or the maximum attempt count has been reached
                GPIO.output(self.hardware_reset_pin, GPIO.LOW)
                time.sleep(self.hardware_reset_wait_period)
                GPIO.output(self.hardware_reset_pin, GPIO.HIGH)
                if self.ready():
                    reset_successful = True
                    break
            GPIO.cleanup()

            if not reset_successful:
                raise ModemError('Failed to reset modem after '
                                 f'{self.hardware_reset_max_attempts} attempts!')
        else:
            self.log('RPi GPIO library is not loaded, skipping hardware reset.')
            if not self.ready():
                raise ModemError('Modem not ready')
