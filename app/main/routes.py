import os
import uuid
import tempfile
import zipfile
import mimetypes
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from firebase_admin import storage
from app import db
from app.main import bp
from app.main.forms import ProfileSettingsForm, EditGameForm
from app.models import User, Game, Upload, Screenshot, Tag


@bp.route('/')
def index():
    games = db.session.scalars(db.select(Game).order_by(Game.created_at.desc())).all()
    return render_template('index.html', games=games)


@bp.route('/user/<username>')
def user(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    games = db.session.scalars(user.games.select().order_by(Game.created_at.desc())).all()
    return render_template('user.html', user=user, games=games)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ProfileSettingsForm()
    if form.validate_on_submit():
        current_user.website = form.website.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.settings'))
    elif request.method == 'GET':
        form.website.data = current_user.website
        form.about.data = current_user.about
    return render_template('settings_profile.html', form=form)


@bp.route('/game/<id>', defaults={'slug': None})
@bp.route('/game/<id>/<slug>')
def game(id, slug):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    if not slug or slug != game.slug:
        return redirect(url_for('main.game', id=game.id, slug=game.slug))
    screenshots = db.session.scalars(game.screenshots.select().order_by(Screenshot.order.asc())).all()
    return render_template('game.html', game=game, screenshots=screenshots)


@bp.route('/game/new', methods=['GET', 'POST'])
@login_required
def new_game():
    form = EditGameForm()
    if form.validate_on_submit():
        if not form.upload.data or not form.cover.data:
            flash('Game file upload and cover image are required')
            return render_template('edit_game.html', form=form)
        game = Game(title=form.title.data, tagline=form.tagline.data, description=form.description.data, creator=current_user)

        folder_name = uuid.uuid4()
        bucket = storage.bucket()

        cover = form.cover.data
        filepath = f'{folder_name}/cover{os.path.splitext(cover.filename)[1]}'
        blob = bucket.blob(filepath)
        blob.upload_from_string(cover.stream.read())
        game.cover_url = blob.public_url

        if form.web_build.data:
            with tempfile.TemporaryDirectory() as temp_dir:
                upload_filepath = os.path.join(temp_dir, secure_filename(form.upload.data.filename))
                form.upload.data.save(upload_filepath)
                with zipfile.ZipFile(upload_filepath) as zip_file:
                    zip_file.extractall(temp_dir)
                os.unlink(upload_filepath)
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        relpath = os.path.relpath(filepath, start=temp_dir)
                        with open(filepath, 'rb') as file_data:
                            blob = bucket.blob(f'{folder_name}/upload/{relpath}')
                            blob.upload_from_file(file_data, content_type=mimetypes.guess_type(filepath)[0])

            blob = bucket.blob(f'{folder_name}/upload/index.html')
            upload = Upload(url=blob.public_url, game=game, web_build=True, size=0)
            db.session.add(upload)
        else:
            game_file = form.upload.data
            filepath = f'{folder_name}/upload/{secure_filename(game_file.filename)}'
            blob = bucket.blob(filepath)
            blob.upload_from_string(game_file.stream.read())
            upload = Upload(url=blob.public_url, game=game, web_build=False, size=0)
            db.session.add(upload)

        if form.screenshots.data:
            for index, file in enumerate(form.screenshots.data):
                filepath = f'{folder_name}/screenshots/{secure_filename(file.filename)}'
                blob = bucket.blob(filepath)
                blob.upload_from_string(file.stream.read())
                screenshot = Screenshot(url=blob.public_url, order=index, game=game)
                db.session.add(screenshot)

        tags_str = form.tags.data
        if tags_str:
            tags = {tag.strip() for tag in tags_str.lower().split(',') if tag.strip()}

            for tag_name in tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                game.tags.append(tag)

        db.session.add(game)
        db.session.commit()

        flash('Your game has been created')
        return redirect(url_for('main.game', id=game.id))
    return render_template('edit_game.html', form=form)


@bp.route('/game/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_game(id):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    if game.creator != current_user:
        return redirect(url_for('main.game', id=game.id))
    form = EditGameForm()
    if form.validate_on_submit():
        game.title = form.title.data
        game.tagline = form.tagline.data
        game.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.game', id=game.id))
    elif request.method == 'GET':
        form.title.data = game.title
        form.tagline.data = game.tagline
        form.description.data = game.description
    return render_template('edit_game.html', form=form, game=game)
