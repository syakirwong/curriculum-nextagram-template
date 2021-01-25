import os
import boto3, botocore
from flask import Blueprint, render_template, request, flash, redirect, url_for, session,  escape
from flask_login import login_required, current_user
from models.user import User
from models.image import Image
from app import app
import peewee as pw

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
    user = User.get_or_none(User.username == username)
    if session['username'] == username and 'username' in session:
        return render_template('users/user_profile.html', username=username, user=current_user, domain=app.config.get('AWS_DOMAIN'), images = pw.prefetch(Image.select().where(Image.user_id == current_user.id), User))

    return render_template("users/user_profile.html",user=user, username=user.username, domain=app.config.get('AWS_DOMAIN'), images = pw.prefetch(Image.select().where(Image.user_id == user.id), User))

@users_blueprint.route('/', methods=["GET"])
def index():
    users = User.select()
    return render_template('home.html', users=users)

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

@users_blueprint.route('/<following_id>/follow', methods=['POST'])
@login_required
def follow(following_id):
    following = User.get_by_id(following_id)

    if current_user.follow(following):
        if current_user.follow_status(following).is_approved:
            flash(f"You follow {following.username}", "primary")
        else:
            flash(f"You send request to follow {following.username}", "primary")
        return redirect(url_for('users.show', username=following.username))
    else:
        flash(f"Unable to follow this user, try again", "danger")
        return redirect(url_for('users.show', username=following.username))

@users_blueprint.route('/<following_id>/unfollow', methods=['POST'])
@login_required
def unfollow(following_id):
    following = User.get_by_id(following_id)

    if current_user.unfollow(following):
        flash(f"You no longer follow {following.username}", "primary")
        return redirect(url_for('users.show', username=following.username))
    else:
        flash(f"Unable to unfollow this user, try again", "danger")
        return redirect(url_for('users.show', username=following.username))


@users_blueprint.route('/<id>/private', methods=['POST'] )
@login_required
def change_privacy(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user.id == int(id):
            privacy = User(id=user.id, username=user.username, password_nohash='Password1111!', is_private=not user.is_private)
            # user.is_private = not user.is_private
            if privacy.save(only=[User.is_private]):
                flash("Successfully updated privacy setting", "success")
                return redirect(url_for("users.show", username = user.username))
            else:
                flash("Failed to update privacy setting", "success")
                return redirect(url_for("users.show", username = user.username))
    else:
        flash("Cannot change setting for another user", "danger")
        return redirect(url_for("users.show", username = user.username))