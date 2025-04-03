from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_password_reset_token()
    send_email(
        '[scratch] Reset Your Password',
        current_app.config['ADMINS'][0],
        [user.email],
        render_template('email/reset_password.txt', user=user, token=token),
        render_template('email/reset_password.html', user=user, token=token)
    )
