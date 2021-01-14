from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
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
    hashed_password = generate_password_hash(password)

    # if len(password) < 8 or len(password) > 50:
    #     flash("Password must be between 8 and 50 characters")
    # if len(password) < 8 or len(password) > 50:
    #     return render_template('users/new.html', errors=['Password must be between 8 and 50 characters'])

    new_user = user.User(username=username, email=email, password=hashed_password)


    if new_user.save():
        flash('Succesfully signed up! Please login using your account.')
        return redirect(url_for('home'))
    else:
        return render_template('users/new.html', username=username, email=email, password=password, errors=new_user.errors)


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
