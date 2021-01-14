from flask import Blueprint, render_template, request, flash, redirect, url_for, session,  escape
from flask_login import login_required
from models import user


users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/', methods=['POST'])
def create():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    new_user = user.User(username=username, email=email, password_nohash=password)

    if new_user.save():
        flash('Succesfully signed up! Please login using your account.')
        return redirect(url_for('login'))
    else:
        return render_template('users/new.html', errors=new_user.errors)


@users_blueprint.route('/<username>', methods=["GET"])
@login_required
def show(username):
    if session['username'] == username and 'username' in session:
        return render_template('users/user_profile.html', username=username)

    return render_template('403.html'), 403


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
