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

    def ready(self):
        # Check modem status
        __, matched = self.console.send('AT', match='OK')
        if not matched:
            return False

        # Check sim ready
        __, matched = self.console.send('AT+CPIN?', match='\+CPIN: READY')
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
        __, matched = self.console.send('AT+CPAS', match='CPAS: [0-9]+')
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
        recieved, matched = self.console.send(
            cmd='AT+CLIP=1', match='\+CLIP: "\+{0,1}[0-9]+"', timeout=timeout)
        if not matched:
            return None

        substr = re.findall('\+{0,1}[0-9]+', matched)
        if not substr or len(substr) == 0:
            raise RuntimeError('Invalid regex match')
        caller = substr[0]

        self.log('Answering incoming call from {}'.format(caller))

        # Answer call
        recieved, matched = self.console.send('ATA', match='OK')

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

        __, matched = self.console.send('ATH', match='OK')
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

        recieved, matched = self.console.send('ATD{};'.format(number),
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

    def call_recording_start(self):
        raise NotImplementedError

    def call_recording_stop(self):
        raise NotImplementedError

    def send_sms(self, number, message):
        '''
        Send the SMS message @message to @number
        '''
        if not self.ready():
            self.error('Modem not ready', ModemError)

        # Set SMS to text mode
        __, matched = self.console.send('AT+CMGF=1', match='OK')
        if not matched:
            self.error('Failed to set SMS mode to text', ModemError)

        # Start writing text
        __, matched = self.console.send('AT+CMGS="{}"'.format(number), match='>')
        if not matched:
            self.error('SMS start command failed', ModemError)
        __, matched = self.console.send('{}\x1A'.format(message),
            match='CMGS', timeout=20)
        if not matched:
            self.error('Failed to send SMS', ModemError)

        self.log('SMS sent')

