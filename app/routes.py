from urllib.parse import urlsplit
from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegisterForm, ProfileSettingsForm, EditGameForm
from app.models import User, Game


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
def user(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    return render_template('user.html', user=user)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ProfileSettingsForm()
    if form.validate_on_submit():
        current_user.website = form.website.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        form.website.data = current_user.website
        form.about.data = current_user.about
    return render_template('settings.html', form=form)


@app.route('/game/new', methods=['GET', 'POST'])
@login_required
def new_game():
    form = EditGameForm()
    if form.validate_on_submit():
        game = Game(title=form.title.data, tagline=form.tagline.data, description=form.description.data, creator=current_user)
        db.session.add(game)
        db.session.commit()
        flash('Your game has been created')
        return redirect(url_for('game', id=game.id))
    return render_template('edit_game.html', form=form)


@app.route('/game/<id>')
def game(id):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    return render_template('game.html', game=game)


@app.route('/game/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_game(id):
    game = db.first_or_404(db.select(Game).where(Game.id == id))
    if game.creator != current_user:
        return redirect(url_for('game', id=game.id))
    form = EditGameForm()
    if form.validate_on_submit():
        game.title = form.title.data
        game.tagline = form.tagline.data
        game.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('game', id=game.id))
    elif request.method == 'GET':
        form.title.data = game.title
        form.tagline.data = game.tagline
        form.description.data = game.description
    return render_template('edit_game.html', form=form)
