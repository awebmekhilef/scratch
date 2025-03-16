from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, URL
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(db.select(User).where(User.username == username.data))
        if user:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        user = db.session.scalar(db.select(User).where(User.email == email.data))
        if user:
            raise ValidationError('Email already exists')


class ProfileSettingsForm(FlaskForm):
    website = StringField('Website', validators=[URL()])
    about = TextAreaField('About', validators=[Length(min=0, max=1000)])
    submit = SubmitField('Save')
