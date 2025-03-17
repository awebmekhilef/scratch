from flask import render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.main.forms import ProfileSettingsForm, EditGameForm
from app.models import User, Game


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/user/<username>')
def user(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    return render_template('user.html', user=user)


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
    return render_template('settings.html', form=form)


@bp.route('/game/new', methods=['GET', 'POST'])
@login_required
def new_game():
    form = EditGameForm()
    if form.validate_on_submit():
        game = Game(title=form.title.data, tagline=form.tagline.data, description=form.description.data, creator=current_user)
        db.session.add(game)
        db.session.commit()
        flash('Your game has been created')
        return redirect(url_for('main.game', id=game.id))
    return render_template('edit_game.html', form=form)


@bp.route('/game/<id>')
def game(id):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    return render_template('game.html', game=game)


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
    return render_template('edit_game.html', form=form)
