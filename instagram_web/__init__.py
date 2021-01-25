from app import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from .util.assets import bundles
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.images.views import images_blueprint
from instagram_web.util.google_oauth import oauth
from flask_assets import Environment, Bundle
from models.user import User
from werkzeug.security import check_password_hash

assets = Environment(app)
assets.register(bundles)
login_manager = LoginManager()
login_manager.init_app(app)
oauth.init_app(app)


app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(images_blueprint, url_prefix="/images")

login_manager.login_view = "login"
login_manager.login_message_category = "error"

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def internal_server_error(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def internal_server_error(e):
    return render_template('404.html'), 404

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/', methods=['GET', 'POST'])
def home():
    users = User.select()
    return render_template('home.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password_to_check = request.form['password']
        user = User.get(User.username == username)

        hashed_password = user.password

        result = check_password_hash(hashed_password, password_to_check)

        if result:
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            login_user(user)
            return redirect(url_for('users.show', username=username))
        else:
            flash('Wrong password!')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    session.pop('password', None)

    return redirect(url_for('login'))

@app.route("/google_login")
def google_login():
    redirect_uri = url_for('authorize', _external = True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/authorize/google")
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    print(user.username)
    if user:
        login_user(user)
        session['username'] = user.username
        return redirect(url_for('users.show', username=user.username))
    else:
        flash("Login failed. Please try again!", "error")
        return redirect('/login')
