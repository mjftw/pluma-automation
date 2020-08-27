import os
import json
import traceback
import platform
from datetime import datetime
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email import encoders


DEFAULT_SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, 'email_settings.json')


class EmailError(Exception):
    pass


class EmailInvalidSettingsError(EmailError):
    pass


class Email():
    """ Create and send emails """
    def __init__(self,
                 to=[],
                 cc=[],
                 bcc=[],
                 subject=None,
                 body=None,
                 body_type='plain',
                 files=[],
                 images=[],
                 images_inline=False,
                 smtp_server=None,
                 smtp_timeout=None,
                 settings_file=None,
                 smtp_password=None,
                 smtp_username=None
                 ):

        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.body = body
        self.body_type = body_type
        self.files = files
        self.images = images
        self.images_inline = images_inline

        self.smtp_password = None
        self.smtp_username = None
        self.smtp_server = None
        self.smtp_timeout = None

        if settings_file and not os.path.isfile(settings_file):
            self.error(f'Cannot open settings file {settings_file}')

        if not settings_file and os.path.isfile(DEFAULT_SETTINGS_FILE):
            settings_file = DEFAULT_SETTINGS_FILE

        if settings_file:
            self.load_settings_file(settings_file)

        # Priorities are: Arguments, file options
        if smtp_password:
            self.smtp_password = smtp_password
        if smtp_username:
            self.smtp_username = smtp_username

        # SMTP Username is also used as send sender email address

        # Priorities are: Arguments, file options, default options
        self.smtp_server = smtp_server or self.smtp_server or 'smtp.office365.com'
        self.smtp_timeout = smtp_timeout or self.smtp_timeout or 587

    def load_settings_file(self, file):
        self.log(f"Attempting to load email settings from file {file}")
        with open(file, 'r') as f:
            settings = json.load(f)

        # Required settings
        if 'smtp' not in settings:
            raise EmailInvalidSettingsError(f'No SMTP settings in file: {file}')
        if 'email' not in settings['smtp']:
            raise EmailInvalidSettingsError(f'No SMTP email in settings file: {file}')
        if 'password' not in settings['smtp']:
            raise EmailInvalidSettingsError(f'No SMTP password in settings file: {file}')

        self.smtp_username = settings['smtp']['email']
        self.smtp_password = settings['smtp']['password']

        # Optional settings
        if 'server' in settings['smtp']:
            self.smtp_server = settings['smtp']['server']
        if 'timeout' in settings['smtp']:
            self.smtp_timeout = settings['smtp']['timeout']

    # Property setters for data sanitation
    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, cc):
        if cc is None:
            self._cc = None
        else:
            if isinstance(cc, str):
                cc = [cc]
            self._cc = list(map(str, cc))

    @property
    def bcc(self):
        return self._bcc

    @bcc.setter
    def bcc(self, bcc):
        if bcc is None:
            self._bcc = None
        else:
            if isinstance(bcc, str):
                bcc = [bcc]
            self._bcc = list(map(str, bcc))

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, to):
        if to is None:
            self._to = None
        else:
            if isinstance(to, str):
                to = [to]
            self._to = list(map(str, to))

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        if body is None:
            self._body = None
        else:
            if not isinstance(body, str):
                body = str(body)
            self._body = body

    @property
    def body_type(self):
        return self._body_type

    @body_type.setter
    def body_type(self, body_type):
        if body_type is None:
            self._body_type = None
        else:
            if not isinstance(body_type, str):
                body_type = str(body_type)
            self._body_type = body_type

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, subject):
        if subject is None:
            self._subject = None
        else:
            if not isinstance(subject, str):
                subject = str(subject)
            self._subject = subject

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, files):
        if files is None:
            self._files = None
        else:
            if isinstance(files, str):
                files = [files]
            self._files = list(map(str, files))

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, images):
        if images is None:
            self._images = None
        else:
            if isinstance(images, str):
                images = [images]
            self._images = list(map(str, images))

    @property
    def smtp_server(self):
        return self._smtp_server

    @smtp_server.setter
    def smtp_server(self, smtp_server):
        if smtp_server is None:
            self._smtp_server = None
        else:
            if not isinstance(smtp_server, str):
                smtp_server = str(smtp_server)
            self._smtp_server = smtp_server

    @property
    def smtp_password(self):
            return self._smtp_password

    @smtp_password.setter
    def smtp_password(self, smtp_password):
        if smtp_password is None:
            self._smtp_password = None
        else:
            if not isinstance(smtp_password, str):
                smtp_password = str(smtp_password)
            self._smtp_password = smtp_password

    @property
    def smtp_username(self):
        if self._smtp_username:
            return self._smtp_username

    @smtp_username.setter
    def smtp_username(self, smtp_username):
        if smtp_username is None:
            self._smtp_username = None
        else:
            if not isinstance(smtp_username, str):
                smtp_username = str(smtp_username)
            self._smtp_username = smtp_username

    def log(self, message):
        """ Very basic logging function. Should change in future """
        print(message)

    def error(self, message, exception=None):
        """ Very basic error function. Should change in future """
        self.log('ERROR: {}'.format(message))
        if exception:
            raise exception(message)

    def send(self):
        """ Validate settings, compose message, and send """
        self._validate()

        msg = self._compose()
        try:
            self._send(msg)
        except smtplib.SMTPException as e:
            self.error(str(e))
            raise(e)


    def _send(self, msg):
        """ Send email with current settings """
        with smtplib.SMTP(self.smtp_server, self.smtp_timeout) as smtp:
            smtp.starttls()
            smtp.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()

            recipients = self.to
            if self.cc:
                recipients.extend(self.cc)
            if self.bcc:
                recipients.extend(self.bcc)

            smtp.sendmail(self.smtp_username, recipients, text)

    def _compose(self):
        """ Combine saved settings into a MIME multipart message """
        msg = MIMEMultipart('mixed')
        msg.preamble = 'This is a multi-part message in MIME format.'

        msg['To'] = ', '.join(self.to)

        if self.cc:
            msg['Cc'] = ', '.join(self.cc)

        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)

        msg['From'] = self.smtp_username
        msg['Subject'] = self.subject

        msg.attach(MIMEText(self.body, self.body_type))

        attachments = self._make_attachments()

        for a in attachments:
            msg.attach(a)

        return msg

    def _validate(self):
        """ Check email has all required settings """

        if not self.to:
            self.error("To address is not set", EmailInvalidSettingsError)
        if not self.smtp_username:
            self.error("smtp username not set", EmailInvalidSettingsError)
        if not self.smtp_password:
            self.error("smtp password not set", EmailInvalidSettingsError)
        if not self.smtp_server:
            self.error("smtp server not set", EmailInvalidSettingsError)
        if not self.smtp_timeout:
            self.error("smtp timeout not set", EmailInvalidSettingsError)

        # Check all attachments exist
        for a in self.files + self.images:
            if not os.path.isfile(a):
                self.error(f"Cannot find file to attach: {a}", EmailInvalidSettingsError)


    def _make_attachments(self):
        """ Create attachment parts for files and images

        if self.images_inline is True, then inline html for the image
        is inserted

        returns a list of attachment parts
        """

        attachments = []

        for f in self.files:
            # Attach files as attachments
            try:
                with open(f, 'rb') as fp:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(fp.read())
            except IOError:
                self.error("Could not file for attachment: {}".format(f))
                continue

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                "attachment; filename={}".format(os.path.basename(f)))
            attachments.append(part)

        for i in self.images:
            # Attach images
            ibn = os.path.basename(i)
            cid = 'image_{}'.format(ibn.replace('.', '_'))
            try:
                with open(i, 'rb') as fp:
                    part = MIMEImage(fp.read(), name=ibn)
            except IOError:
                self.error("Could not image for attachment: {}".format(i))
                continue

            part.add_header('Content-ID', '<{}>'.format(cid))
            attachments.append(part)
            if self.images_inline:
                attachments.append(MIMEText(
                    u'<img src="cid:{}" alt="{}">'.format(cid, ibn),
                    'html', 'utf-8')
                )
        return attachments


def send_exception_email(exception, recipients=None, board=None,
        subject=None, prepend_body=None, settings_file=None):
    settings_file = settings_file or DEFAULT_SETTINGS_FILE
    if not recipients:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            if 'maintainers' not in settings:
                raise EmailInvalidSettingsError(
                    'recipents not given and "maintainers" not in settings file: {}'.format(
                        settings_file))
            recipients = settings['maintainers']

    email = Email(
        to=recipients,
        files=[],
        body='',
        body_type='html'
    )

    error_info = {
        'exception': exception.__class__.__name__,
        'cause': str(exception),
        'time': datetime.now().strftime('%d-%m-%y %H:%M:%S'),
        'trace': traceback.format_exc()
        }

    if prepend_body:
        email.body += '{}<br><hr><br>'.format(prepend_body)

    email.body += '''
        <b>Exception:</b> {}<br>
        <b>Cause:</b> {}<br>
        <b>Time:</b> {}<br>
        <b>Trace:</b> {}<br>
        <hr>
        '''.format(
            error_info['exception'],
            error_info['cause'],
            error_info['time'],
            '<br>'.join(error_info['trace'].split('\n')))

    email.body += '''
        <b>Platform: </b>{}<br><hr>
        '''.format('<br>'.join(list(str(platform.uname()).split(','))))

    if subject:
        email.subject = subject
    else:
        email.subject = 'Unhandled Exception Occured: [{}]'.format(
            error_info['exception'])
        if board:
            email.subject =('{} [{}]'.format(email.subject, board.name))

    if board:
        email.body += '<b>Board Info:</b><br>'
        email.body += '<br>'.join(board.show_hier().split('\n'))
        email.body += '<hr><br>'

        email.files.append(board.log_file)
        if board.console and board.console.log_file:
            email.files.append(board.console.log_file)

        board.log(email.subject, color='red', bold=True)
        board.log(str(error_info), color='red', bold=True)
        board.log('Informing lab maintainers via email')

    email.send()
