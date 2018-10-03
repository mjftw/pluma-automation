#!/usr/bin/env python3

import smtplib
from os import path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders


class InvalidEmailSettings(Exception):
    pass


class email():
    def __init__(
        self,
        addr_to=[],
        addr_from="",
        subject="",
        body="",
        attach_files=[],
        smtp_server="",
        smtp_user="",
        smtp_pass="",
        smtp_timeout=587,
    ):
        self.addr_to = addr_to
        self.addr_from = addr_from,
        self.subject = subject
        self.body = body
        self.attach_files = attach_files

        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        if(smtp_user != ""):
            self.smtp_user = smtp_user
        else:
            self.smtp_user = addr_from
        self.smtp_pass = smtp_pass
        self.smtp_timeout = smtp_timeout

    def send():
        if(
            self.addr_to == "" or
            self.addr_from == [] or
            self.smtp_server == "" or
            self.smtp_user == "" or
            self.smtp_pass == ""
        ):
            raise Exception(InvalidEmailSettings)

        msg = MIMEMultipart()

        msg['From'] = self.addr_from
        msg['To'] = '; '.join(self.addr_to)
        msg['Subject'] = self.subject
        msg.preamble = 'This is a multi-part message in MIME format.'

        msg.attach(MIMEText(body, 'html'))

        for filename in self.attach_files:
            attachment = open(filename, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s"
                            % filename)
            msg.attach(part)

        server = smtplib.SMTP(self.smtp_user, self.smtp_timeout)
        server.starttls()
        server.login(self.addr_from, self.smtp_pass)
        text = msg.as_string()
        server.sendmail(self.addr_from, self.to_addrs, text)
        server.quit()
