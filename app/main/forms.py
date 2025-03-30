from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField, FileAllowed
from wtforms import StringField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, URL


class ProfileSettingsForm(FlaskForm):
    website = StringField('Website', validators=[URL()])
    about = TextAreaField('About')
    submit = SubmitField('Save')


class EditGameForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    tagline = StringField('Tagline')
    tags = StringField('Tags (comma separated)')
    description = TextAreaField('Description')
    uploads = MultipleFileField('Uploads')
    uploads_metadata = HiddenField('')
    cover = FileField('Cover Image')
    screenshots = MultipleFileField('Screenshots', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField('Save')


class CommentForm(FlaskForm):
    comment = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
