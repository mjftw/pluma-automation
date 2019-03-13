import time
import re

from .serialconsole import SerialConsole
from .farmclass import Farmclass


class ModemError(Exception):
    pass


class ModemSim868(Farmclass):
    ''' Diver for the Sim868 based GSM/GNSM/GPS/Bluetooth modem '''
    def __init__(self, port):
        ''' @port: Port of the serial console for sending AT commands '''
        self.console = SerialConsole(port, 115200)

        self._recording_lock = False

    def AT_send(self, *args, **kwargs):
        if self._recording_lock:
            self.error('Cannot send AT commands while recording in progress',
                ModemError)

        return self.console.send(*args, **kwargs)

    def ready(self):
        # Check modem status
        __, matched = self.AT_send('AT', match='OK')
        if not matched:
            return False

        # Check sim ready
        __, matched = self.AT_send('AT+CPIN?', match='\+CPIN: READY')
        if not matched:
            return False

        return True

    def _phone_activity_status(self):
        '''
        Return phone activity status.
            0: Ready
            2: Unknown
            3: Incoming call
            4: Ongoing call
        '''
        if not self.ready():
            self.error('Modem not ready', ModemError)

        __, matched = self.AT_send('AT+CPAS', match='CPAS: [0-9]+')
        if not matched:
            self.error('Incorrect response from modem', ModemError)

        substr = re.findall('[0-9]+', matched)
        if not substr or len(substr) == 0:
            raise RuntimeError('Invalid regex match')

        return substr[0]

    def ongoing_call(self):
        ''' If call ongoing, return True, else return False'''
        if self._phone_activity_status() == '4':
            return True
        else:
            return False

    def incoming_call(self):
        ''' If call incoming, return True, else return False'''
        if self._phone_activity_status() == '3':
            return True
        else:
            return False

    def answer_call(self, timeout=30, record=False):
        '''
        Expect a call withing the next @timeout seconds, and answer when
        it comes through. If record the call if @record is set.
        If there is an ongoing call, it is ended.
        Returns None if no call recieved in @timeout seconds.
        Returns phone number of caller if call recieved
        '''
        if self.ongoing_call():
            self.log('Ending ongoing call')
            self.end_call()

        if not self.ready():
            self.error('Modem not ready', ModemError)

        # Enable call notification and wait for incoming
        recieved, matched = self.AT_send(
            cmd='AT+CLIP=1', match='\+CLIP: "\+{0,1}[0-9]+"', timeout=timeout)
        if not matched:
            return None

        substr = re.findall('\+{0,1}[0-9]+', matched)
        if not substr or len(substr) == 0:
            raise RuntimeError('Invalid regex match')
        caller = substr[0]

        self.log('Answering incoming call from {}'.format(caller))

        # Answer call
        recieved, matched = self.AT_send('ATA', match='OK')

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
            self.error('Modem not ready', ModemError)

        if self.ongoing_call():
            self.log('Cannot make call, call ongoing')
            return False

        self.log('Calling {}'.format(number))

        recieved, matched = self.AT_send('ATD{};'.format(number),
            match=['OK', 'NO DIALTONE', 'BUSY', 'NO CARRIER', 'NO ANSWER'],
            excepts='ERROR')
        if not matched:
            self.error('Unexpected response from modem: {}'.format(recieved),
                ModemError)

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
        Starting recording stops AT commands from being sent unil recording stops.
        '''
        if self.call_recording_ongoing():
            self.log('Cannot start recording, recording in progress')
            return False

        # Start a recording, with data sent at a 100ms interval,
        # and a no sent at the end of transmission.
        # __, matched = self.AT_send('AT+CRECORD=1,5,2', #last 2 bytes are crc
        __, matched = self.AT_send('AT+CRECORD=1,5,0',
            match=['OK', 'CRECORD'], excepts='ERROR')
        if not matched:
            self.error('Failed to start recording', ModemError)

        # Flush serial input buffer
        self.console.flush(True)

        # From this point, direcly interract with Seiral Object
        self._recording_lock = True

        self.log('Started recording. Do not try to send AT commands before stopping')

        return True

    def call_recording_stop(self, file):
        '''
        Stop an ongoing call recording.
        Returns True if recording saved to @file.
        Returns False if no recording is ongoing.
        File format is AMR 4.75k
        '''
        if not self.call_recording_ongoing():
            return False

        serial = self.console._ser

        # Write any data to serial to stop recording
        serial.write(self.console.encode('0'))

        data = serial.readall()
        self._recording_lock = False

        # Strip out AT commands from start and end of data
        if data.startswith(self.console.encode('\r\n+CRECORD:')):
            data = data[len('\r\n+CRECORD:'):]
        if data.endswith(self.console.encode('\r\nOK\r\n')):
            data = data[:-len('\r\nOK\r\n')]

        packets = []

        with open(file, 'wb') as f:
            # Write AMR file header
            f.write(b'#*AMR\n')
            f.write(data)

            # Split data by packet header 0x7E
            # for p in [p for p in data.split(b'\x7E') if p]:
            #     # Fix replaced bytes
            #     p.replace(b'\x7D\x5E', b'\x7E')
            #     p.replace(b'\x7D\x5D', b'\x7D')
            #     crc = p[-2:]
            #     p = p[:-2]
            #     #TODO: Calculate CRC and check it
            #     f.write(p)

        return True

    def send_sms(self, number, message):
        '''
        Send the SMS message @message to @number
        '''
        if not self.ready():
            self.error('Modem not ready', ModemError)

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
        Returns a list of all SMS messages recieved if @sms_number
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

    def sms_recieved(self):
        '''
        Returns the number of SMS recieved
        '''
        raise NotImplementedError