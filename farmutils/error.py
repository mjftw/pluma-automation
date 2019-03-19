import traceback
import platform
from datetime import datetime

from .email import Email

def send_exception_email(exception, recipients, board=None, subject=None, prepend_body=None):
    email = Email(
        sender='lab@witekio.com',
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

        board.log(email.subject)
        board.log(str(error_info))
        board.log('Informing lab maintainers via email')

    email.send()
