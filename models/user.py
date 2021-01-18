from models.base_model import BaseModel
from werkzeug.security import generate_password_hash
from flask_login import UserMixin, current_user
import peewee as pw
import re


class User(UserMixin, BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(index=True, unique=True)
    password= pw.CharField(null=False)
    password_nohash = None
    profile_picture = pw.CharField()

    def validate(self):
        duplicate_usernames= User.get_or_none(User.username == self.username)
        existing_email = User.get_or_none(User.email == self.email)

        if self.username == "":
            self.errors.append('No username provided')

        if self.email == "":
            self.errors.append('No email provided')

        if self.password == "":
            self.errors.append('Password not provided')

        if duplicate_usernames and self.username != current_user.username:
            self.errors.append('Username already exist. Pick another username.')

        if existing_email:
            self.errors.append('Email already exist. Please login using your existing account.')

        if len(self.password_nohash) < 8 or len(self.password_nohash) > 50:
            self.errors.append('Password must be between 8 and 50 characters')

        if not re.match(r"^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?\W).*$", self.password_nohash):
            self.errors.append('Password must contain at least one uppercase letter, one lowercase letter, one number and one special character')
        else:
            self.password = generate_password_hash(self.password_nohash)
