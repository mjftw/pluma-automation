import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email import encoders

DEFAULT_SMTP = 'smtp.office365.com'
DEFAULT_TIMEOUT = 587


class EmailInvalidSettings(Exception):
    pass


class Email():
    """ Create and send emails """
    def __init__(self):
        self.mail_settings = {}
        self.smtp_settings = {}
        self.attachments = []

    def log(self, message):
        """ Very basic logging function. Should change in future """
        print(message)

    def error(self, message):
        """ Very basic error function. Should change in future """
        self.log('ERROR: {}'.format(message))

    def send(self):
        """ Validate settings, compose message, and send """
        if self._validate():
            msg = self._compose()
            try:
                self._send(msg)
            except smtplib.SMTPException as e:
                self.error(str(e))
                raise(e)
        else:
            self.error("Send failed. Invalid settings.")

    def _send(self, msg):
        """ Send email with current settings """
        with smtplib.SMTP(
                self.smtp_settings['server'],
                self.smtp_settings['timeout']) as smtp:
            smtp.starttls()
            smtp.login(self.mail_settings['from'],
                       self.smtp_settings['password'])
            text = msg.as_string()

            recipients = self.mail_settings['to']
            if self.mail_settings.get('cc'):
                recipients.extend(self.mail_settings['cc'])
            if self.mail_settings.get('bcc'):
                recipients.extend(self.mail_settings['bcc'])

            smtp.sendmail(self.mail_settings['from'], recipients, text)

    def _compose(self):
        """ Combine saved settings into a MIME multipart message """
        msg = MIMEMultipart('mixed')
        msg.preamble = 'This is a multi-part message in MIME format.'

        msg['To'] = ', '.join(self.mail_settings['to'])
        if self.mail_settings.get('cc'):
            msg['Cc'] = ', '.join(self.mail_settings['cc'])
        if self.mail_settings.get('bcc'):
            msg['Bcc'] = ', '.join(self.mail_settings['bcc'])
        msg['From'] = self.mail_settings['from']
        msg['Subject'] = self.mail_settings['subject']

        msg.attach(MIMEText(self.mail_settings['body'], 'html'))

        for a in self.attachments:
            msg.attach(a)

        return msg

    def _validate(self):
        """ Check email has all required settings """
        valid = True

        # Check email settings
        if not self.mail_settings.get('to'):
            self.error("To address is not set")
            valid = False
        if not self.mail_settings.get('from'):
            self.error("From address is not set")
            valid = False

        # Check SMTP settings
        if not self.smtp_settings.get('password'):
            self.error("smtp password not set")
            valid = False
        if not self.smtp_settings.get('server'):
            self.error("smtp server not set")
            valid = False
        if not self.smtp_settings.get('timeout'):
            self.error("smtp timeout not set")
            valid = False

        if not valid:
            raise EmailInvalidSettings

        return valid

    def set_smtp(self, password, server=DEFAULT_SMTP, timeout=DEFAULT_TIMEOUT):
        """ Set SMTP email settings """
        self.smtp_settings['password'] = password
        self.smtp_settings['server'] = server
        self.smtp_settings['timeout'] = timeout

    def set_addr(self, to_addr, from_addr, cc_addr=None, bcc_addr=None):
        """ Set sender and recipents email settings """
        self.mail_settings['from'] = from_addr

        if isinstance(to_addr, str):
            to_addr = [to_addr]
        self.mail_settings['to'] = to_addr

        if cc_addr:
            if isinstance(cc_addr, str):
                cc_addr = [cc_addr]
            self.mail_settings['cc'] = cc_addr

        if bcc_addr:
            if isinstance(bcc_addr, str):
                bcc_addr = [bcc_addr]
            self.mail_settings['bcc'] = bcc_addr

    def set_text(self, subject=None, body=None):
        """ Set subject and body of email """
        self.mail_settings['body'] = body
        self.mail_settings['subject'] = subject

    def set_attachments(self, files=None, images=None, inline=False):
        """ Attach files and images

        files -- Files are attached as plain attachments.
        images -- Images are attached, & inline HTML inserted (if inline=True).
        """

        # Clear old attachments
        self.attachments = []

        if isinstance(files, str):
            files = [files]
        for f in files:
            # Attach files as attachments
            try:
                with open(f, 'rb') as fp:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(fp.read())
            except IOError:
                self.error("Could not file for attachment: {}".format(f))
                continue

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename={}".format(
                os.path.basename(f)))
            self.attachments.append(part)

        if isinstance(images, str):
            images = [images]
        for i in images:
            # Attach images inline
            ibn = os.path.basename(i)
            cid = 'image_{}'.format(ibn.replace('.', '_'))
            try:
                with open(i, 'rb') as fp:
                    part = MIMEImage(fp.read(), name=ibn)
            except IOError:
                self.error("Could not image for attachment: {}".format(i))
                continue

            part.add_header('Content-ID', '<{}>'.format(cid))
            self.attachments.append(part)
            if inline:
                self.attachments.append(MIMEText(
                    u'<img src="cid:{}" alt="{}">'.format(cid, ibn), 'html', 'utf-8'))


def newemail(subject="", body="", files=[], me=False):
    """ Glue function for backwards compatibility

    This function should be deleted once older scripts
    have been updated to use Email class properly.
    """

    if me:
        recipients = [
            'wsheppard@witekio.com',
            'sheppard.will@gmail.com',
        ]
    else:
        recipients = [
            'wsheppard@witekio.com',
            'amurray@witekio.com',
            'elangley@witekio.com',
            'jeremyr@ovation.co.uk',
        ]

    e = Email()
    e.set_addr(recipients, 'wsheppard@witekio.com')
    e.set_smtp('4T2jsU', 'smtp.office365.com', 587)
    e.set_text(subject, body)
    e.set_attachments(files)
    e.send()
