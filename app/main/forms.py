from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
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
    upload = FileField('Game File Upload', validators=[FileRequired()])
    cover = FileField('Cover Image', validators=[FileRequired()])
    screenshots = MultipleFileField('Screenshots', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Save')
