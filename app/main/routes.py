import os
import uuid
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
        game = Game(title=form.title.data, tagline=form.tagline.data, description=form.description.data, creator=current_user)

        folder_name = uuid.uuid4()
        bucket = storage.bucket()

        cover = form.cover.data
        filepath = f'{folder_name}/cover{os.path.splitext(cover.filename)[1]}'
        blob = bucket.blob(filepath)
        blob.upload_from_string(cover.stream.read())
        game.cover_url = blob.public_url

        game_file = form.upload.data
        filepath = f'{folder_name}/upload/{secure_filename(game_file.filename)}'
        blob = bucket.blob(filepath)
        blob.upload_from_string(game_file.stream.read())
        upload = Upload(url=blob.public_url, game=game, size=0)
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
