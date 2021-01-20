import os
import boto3, botocore
from flask import Blueprint, render_template, request, flash, redirect, url_for, session,  escape
from flask_login import login_required, current_user
from models.user import User
from models.image import Image
import peewee as pw


AWS_DOMAIN = 'http://{}.s3-ap-southeast-1.amazonaws.com/'.format(os.getenv('AWS_BUCKET'))

s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('AWS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET')
    )


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

    new_user = User(username=username, email=email, password_nohash=password, profile_picture='null')

    if new_user.save():
        flash('Succesfully signed up! Please login using your account.')
        return redirect(url_for('login'))
    else:
        return render_template('users/new.html', errors=new_user.errors)


@users_blueprint.route('/<username>', methods=["GET"])
@login_required
def show(username):
    if session['username'] == username and 'username' in session:
        return render_template('users/user_profile.html', username=username, user=current_user, domain=AWS_DOMAIN, images = pw.prefetch(Image.select().where(Image.user_id == current_user.id), User))

@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
        return render_template('users/edit_user_info.html', user=current_user)

@users_blueprint.route('/<id>', methods=['POST'])
@login_required
def update(id):
    new_username = User(id=id, username=request.form['new_username'], password_nohash=request.form['password'])
    file = request.files['new_profile_picture']

    user = User.get_by_id(id)

    if current_user == user:
        s3.upload_fileobj(
            file,
            os.environ["AWS_BUCKET"],
            "user/" + str(user.id)+ "/profile_picture/" + file.filename,
            ExtraArgs = {
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        upload_image = User(id=user.id, username=user.username, password_nohash=request.form['password'], profile_picture=f"user/{str(user.id)}/profile_picture/{file.filename}")
        upload_image.save(only=[User.profile_picture])
        if new_username.save(only=[User.username]):
            session['username'] = request.form['new_username']
            flash("Your new username has been updated!")
        else:
            flash("Could not update new username!")
        return redirect(url_for('users.edit', id=id))

    return redirect(url_for('users.edit', id=id))

@users_blueprint.route('/<id>/request_upload', methods=['GET', 'POST'])
@login_required
def upload_request(id):
    user = User.get_by_id(id)

    if request.method == 'POST':
        if current_user == user:
            file = request.files['image_file']
            s3.upload_fileobj(
            file,
            os.environ["AWS_BUCKET"],
            "user/" + str(user.id) + "/uploaded_image/" + file.filename,
            ExtraArgs = {
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )
            upload_image = Image(user_id=user.id, photo_url=f"user/{str(user.id)}/uploaded_image/{file.filename}")
            if upload_image.save():
                flash("Succesfully uploaded!")
                return redirect(url_for('users.show', username=user.username))
            else:
                flash("Upload failed!")

    return render_template('users/upload_image.html', user=user)

@users_blueprint.route('/<id>/upload', methods=['GET', 'POST'])
@login_required
def upload(id):
    user = User.get_by_id(id)
    return render_template('users/upload_image.html', user=user)