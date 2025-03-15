from flask import render_template, redirect, flash
from app import app
from app.forms import LoginForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'User {form.username.data} successfully logged in.')
        return redirect('/')
    return render_template('login.html', form=form)
