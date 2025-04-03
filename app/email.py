from threading import Thread
from flask import current_app
from flask_mailman import EmailMultiAlternatives


def send_async_email(app, msg):
    with app.app_context():
        msg.send()


def send_email(subject, sender, recipients, body, html):
    msg = EmailMultiAlternatives(subject, body, sender, recipients)
    msg.attach_alternative(html, 'text/html')
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
