from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL


class ProfileSettingsForm(FlaskForm):
    website = StringField('Website', validators=[URL()])
    about = TextAreaField('About')
    submit = SubmitField('Save')


class EditGameForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tagline = StringField('Tagline')
    tags = StringField('Tags')
    description = TextAreaField('Description')
    upload = FileField('Game File Upload')
    web_build = BooleanField("Web build")
    cover = FileField('Cover Image')
    screenshots = MultipleFileField('Screenshots', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Save')
