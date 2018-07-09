#!/usr/bin/env python3

import smtplib
from os import path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders


def newemail(subject="", body="", files=[], me=False):
    fromaddr = "wsheppard@witekio.com"

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

    msg = MIMEMultipart('mixed')

    msg['From'] = fromaddr
    msg['To'] = '; '.join(recipients)
    msg['Subject'] = subject
    msg.preamble = 'This is a multi-part message in MIME format.'

    msg.attach(MIMEText(body, 'html'))

    for filename in files:
        bn = path.basename(filename)
        fp = open(filename, "rb")
        img = MIMEImage( fp.read())
        fp.close()
        img.add_header('Content-Disposition', "attachment; filename={}".format(bn))
        #img.add_header( 'Content-ID', '<{}>'.format( bn ) )
        msg.attach(img)

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(fromaddr, "4T2jsU")
    text = msg.as_string()
    server.sendmail(fromaddr, recipients, text)
    server.quit()



def doemail(subject="", body="", files=[]):
    fromaddr = "wsheppard@witekio.com"
    recipients = [
        'wsheppard@witekio.com',
        'amurray@witekio.com',
        'elangley@witekio.com'
    ]

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    #msg['To'] = toaddr
    msg['To'] = '; '.join(recipients)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    for filename in files:
        attachment = open(filename, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(fromaddr, "4T2jsU")
    text = msg.as_string()
    server.sendmail(fromaddr, recipients, text)
    server.quit()
