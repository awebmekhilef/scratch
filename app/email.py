from threading import Thread
from flask import current_app
from flask_mailman import EmailMultiAlternatives


def _send_async_email(app, msg):
    with app.app_context():
        msg.send()


def send_email(subject, sender, recipients, body, html, attachments, sync):
    msg = EmailMultiAlternatives(subject, body, sender, recipients)
    msg.attach_alternative(html, 'text/html')
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        msg.send()
    else:
        Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()
