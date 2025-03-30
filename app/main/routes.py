import os
import json
import uuid
import tempfile
import zipfile
import mimetypes
from flask import render_template, redirect, url_for, flash, current_app, request, g
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from firebase_admin import storage
from app import db
from app.main import bp
from app.main.forms import ProfileSettingsForm, EditGameForm, CommentForm, SearchForm, EmptyForm
from app.models import User, Game, Upload, Screenshot, Tag, Comment


@bp.before_app_request
def before_requrest():
    g.search_form = SearchForm()


@bp.route('/')
def index():
    games = db.session.scalars(db.select(Game).order_by(Game.created_at.desc())).all()
    return render_template('index.html', games=games)


@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    games, total = Game.search(g.search_form.q.data, page, current_app.config['RESULTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['RESULTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', games=games, next_url=next_url, prev_url=prev_url)


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
    return render_template('settings_profile.html', form=form, active_page='profile')


@bp.route('/game/<id>', defaults={'slug': None})
@bp.route('/game/<id>/<slug>')
def game(id, slug):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    if not slug or slug != game.slug:
        return redirect(url_for('main.game', id=game.id, slug=game.slug))
    uploads = db.session.scalars(game.uploads.select()).all()
    screenshots = db.session.scalars(game.screenshots.select().order_by(Screenshot.order.asc())).all()
    comments = db.session.scalars(game.comments.select().order_by(Comment.created_at.desc())).all()
    comment_form = CommentForm()
    delete_comment_form = EmptyForm()
    return render_template('game.html', game=game, uploads=uploads, screenshots=screenshots, comments=comments, comment_form=comment_form, delete_comment_form=delete_comment_form)


@bp.route('/game/new', methods=['GET', 'POST'])
@login_required
def new_game():
    form = EditGameForm()
    if form.validate_on_submit():
        if not form.cover.data:
            flash('Cover image is required')
            return render_template('edit_game.html', form=form)

        game = Game(
            title=form.title.data,
            tagline=form.tagline.data,
            description=form.description.data,
            creator=current_user)

        folder = uuid.uuid4()
        bucket = storage.bucket()

        uploads_metadata = json.loads(form.uploads_metadata.data)
        uploads = form.uploads.data
        if uploads:
            for index, upload_file in enumerate(uploads):
                upload_filename = secure_filename(upload_file.filename)
                is_web_build = uploads_metadata[index].get('is_web_build', False)

                if is_web_build:
                    if os.path.splitext(upload_file.filename)[1] != '.zip':
                        flash('Only .zip files are allowed for web builds', 'error')
                        return render_template('edit_game.html', form=form)

                    with tempfile.TemporaryDirectory() as tmp_dir:
                        upload_filepath = os.path.join(tmp_dir, upload_filename)
                        upload_file.save(upload_filepath)
                        with zipfile.ZipFile(upload_filepath) as zip_file:
                            zip_file.extractall(tmp_dir)
                        os.unlink(upload_filepath)

                        for root, _, files in os.walk(tmp_dir):
                            for file in files:
                                filepath = os.path.join(root, file)
                                relpath = os.path.relpath(filepath, start=tmp_dir)
                                with open(filepath, 'rb') as file_data:
                                    blob = bucket.blob(f'{folder}/uploads/web/{relpath}')
                                    blob.upload_from_file(file_data, content_type=mimetypes.guess_type(filepath)[0])

                                    if relpath == 'index.html':
                                        upload = Upload(url=blob.public_url, filename=relpath, game=game, is_web_build=True, size=0)
                                        db.session.add(upload)
                else:
                    bytes = upload_file.read()
                    blob = bucket.blob(f'{folder}/uploads/{upload_filename}')
                    blob.upload_from_string(bytes, content_type=upload_file.mimetype)
                    upload = Upload(url=blob.public_url, filename=upload_filename, game=game, is_web_build=False, size=len(bytes))
                    db.session.add(upload)

        cover_file = form.cover.data
        if cover_file:
            blob = bucket.blob(f'{folder}/cover{os.path.splitext(cover_file.filename)[1]}')
            blob.upload_from_string(cover_file.read(), content_type=cover_file.mimetype)
            game.cover_url = blob.public_url

        if form.screenshots.data:
            for index, screenshot_file in enumerate(form.screenshots.data):
                blob = bucket.blob(f'{folder}/screenshots/{index}{os.path.splitext(screenshot_file.filename)[1]}')
                blob.upload_from_string(screenshot_file.read(), content_type=screenshot_file.mimetype)
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


@bp.route('/comment/<game_id>', methods=['POST'])
@login_required
def comment(game_id):
    form = CommentForm()
    if form.validate_on_submit():
        game = db.first_or_404(db.select(Game).where(Game.id == game_id))
        comment = Comment(text=form.comment.data, game=game, author=current_user)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('main.game', id=game_id, _anchor='comments'))


@bp.route('/delete_comment/<id>', methods=['POST'])
@login_required
def delete_comment(id):
    form = EmptyForm()
    if form.validate_on_submit():
        comment = db.first_or_404(db.select(Comment).where(Comment.id == id))
        if comment.author != current_user and comment.game.creator != current_user:
            return redirect(url_for('main.index'))
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('main.game', id=comment.game_id, _anchor='comments'))
