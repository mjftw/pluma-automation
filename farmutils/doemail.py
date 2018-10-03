import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email import encoders


class EmailInvalidSettings(Exception):
    pass


class Email():
    """ Create and send emails """
    def __init__(self,
                 sender=None,
                 to=[],
                 cc=[],
                 bcc=[],
                 subject=None,
                 body=None,
                 body_type='plain',
                 files=[],
                 images=[],
                 images_inline=False,
                 smtp_server='smtp.office365.com',
                 smtp_timeout=587,
                 smtp_authfile=None,
                 smtp_password=None,
                 smtp_username=None
                 ):

        self.sender = sender
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.body = body
        self.body_type = body_type
        self.files = files
        self.images = images
        self.images_inline = images_inline

        self.smtp_server = smtp_server
        self.smtp_timeout = smtp_timeout
        self.smtp_authfile = smtp_authfile
        self.smtp_password = smtp_password
        self.smtp_username = smtp_username

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
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, sender):
        if sender is None:
            self._sender = None
        else:
            if not isinstance(sender, str):
                sender = str(sender)
            self._sender = sender

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
        else:
            return self._sender

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
        with smtplib.SMTP(self.smtp_server, self.smtp_timeout) as smtp:
            smtp.starttls()
            if self.smtp_authfile:
                (username, password) = self._read_authfile()
            else:
                username = self.smtp_username
                password = self.smtp_password
            smtp.login(username, password)
            text = msg.as_string()

            recipients = self.to
            if self.cc:
                recipients.extend(self.cc)
            if self.bcc:
                recipients.extend(self.bcc)

            smtp.sendmail(self.sender, recipients, text)

    def _compose(self):
        """ Combine saved settings into a MIME multipart message """
        msg = MIMEMultipart('mixed')
        msg.preamble = 'This is a multi-part message in MIME format.'

        msg['To'] = ', '.join(self.to)

        if self.cc:
            msg['Cc'] = ', '.join(self.cc)

        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)

        msg['From'] = self.sender
        msg['Subject'] = self.subject

        msg.attach(MIMEText(self.body, self.body_type))

        attachments = self._make_attachments()

        for a in attachments:
            msg.attach(a)

        return msg

    def _validate(self):
        """ Check email has all required settings """
        valid = True

        # Check email settings
        if not self.to:
            self.error("To address is not set")
            valid = False
        if not self.sender:
            self.error("From address is not set")
            valid = False

        if self.smtp_authfile:
            try:
                if not self._read_authfile():
                    self.error('Invalid smtp authfile {}'.format(
                        self.smtp_authfile))
            except IOError as e:
                self.error("{}".format(str(e)))
                valid = False
        else:
            if not self.smtp_username:
                self.error("smtp username not set, and no auth file")
                valid = False
            if not self.smtp_password:
                self.error("smtp password not set, and no auth file")
                valid = False

        if not self.smtp_server:
            self.error("smtp server not set")
            valid = False
        if not self.smtp_timeout:
            self.error("smtp timeout not set")
            valid = False

        # Check all attachments exist
        for a in self.files + self.images:
            if not os.path.isfile(a):
                self.error("Cannot find file to attach: {}".format(a))
                valid = False

        if not valid:
            raise EmailInvalidSettings

        return valid

    def _read_authfile(self):
        """ Check smtp authfile has exactly 2 lines.
            Expected authfile format:
                [smtp_username]
                [smtp_password]
        """
        with open(self.smtp_authfile, 'r') as fd:
            auth = fd.read().splitlines()
        if len(auth) != 2 or not auth[0] or not auth[1]:
            return None
        else:
            username = auth[0]
            password = auth[1]
            return (username, password)

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

    Email(sender='wsheppard@witekio.com',
          to=recipients,
          subject=subject,
          body=body,
          body_type='html',
          files=files,
          smtp_server='smtp.office365.com',
          smtp_timeout=587,
          smtp_password='4T2jsU',
          ).send()
