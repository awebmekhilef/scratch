from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import  DataRequired, URL

class ProfileSettingsForm(FlaskForm):
    website = StringField('Website', validators=[URL()])
    about = TextAreaField('About')
    submit = SubmitField('Save')


class EditGameForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tagline = StringField('Tagline')
    description = TextAreaField('Description')
    submit = SubmitField('Save')
