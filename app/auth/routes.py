import qrcode
import qrcode.image.svg
from io import BytesIO
from base64 import b64encode
from urllib.parse import urlsplit
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, UpdatePasswordForm, TwoFactorAuthForm, EmptyForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        if user.is_2fa_enabled:
            session['username'] = user.username
            session['remember'] = form.remember.data
            return redirect(url_for('auth.verify_totp'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)


@bp.route('/login/verify-totp', methods=['GET', 'POST'])
def verify_totp():
    form = TwoFactorAuthForm()
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = db.session.scalar(db.select(User).where(User.username == session['username']))
    if not user:
        return redirect(url_for('auth.login'))
    if form.validate_on_submit():
        if user.verify_totp(form.token.data):
            login_user(user, remember=session.get('remember', False))
            return redirect(url_for('main.index'))
        else:
            flash('Invalid OTP token', 'error')
            return redirect(url_for('auth.verify_totp'))
    return render_template('/auth/verify_2fa.html', form=form, user=user)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been successfully changed')
        else:
            flash('Current password is incorrect' 'error')
        return redirect(url_for('auth.password'))
    return render_template('settings_password.html', form=form, active_page='password')


@bp.route('/settings/two-factor-auth', methods=['GET', 'POST'])
@login_required
def two_factor_auth_setup():
    two_factor_auth_form = TwoFactorAuthForm()
    disable_2fa_from = EmptyForm()
    if two_factor_auth_form.validate_on_submit():
        if current_user.verify_totp(two_factor_auth_form.token.data):
            current_user.is_2fa_enabled = True
            db.session.commit()
            flash('Two factor authentication has been enabled')
        else:
            flash('Invalid OTP token', 'error')
        return redirect(url_for('auth.two_factor_auth_setup'))
    elif disable_2fa_from.validate_on_submit():
        if current_user.is_2fa_enabled:
            current_user.is_2fa_enabled = False
            db.session.commit()
            flash('Two factor authentication has been disabled')
            return redirect(url_for('auth.two_factor_auth_setup'))
    img = qrcode.make(current_user.get_totp_url(), image_factory=qrcode.image.svg.SvgImage, border=0)
    buffer = BytesIO()
    img.save(buffer)
    qrcode_data = b64encode(buffer.getvalue()).decode('utf-8')
    return render_template('settings_2fa.html', active_page='2fa', 
                           two_factor_auth_form=two_factor_auth_form, qrcode_data=qrcode_data, 
                           disable_2fa_from=disable_2fa_from), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
