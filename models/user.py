from models.base_model import BaseModel
import peewee as pw
import re


class User(BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(index=True, unique=True)
    password = pw.CharField(null=False)

    def validate(self):
        duplicate_usernames= User.get_or_none(User.username == self.username)
        existing_email = User.get_or_none(User.email == self.email)
        password = self.password

        if duplicate_usernames:
            self.errors.append('Username already exist. Pick another username.')

        if existing_email:
            self.errors.append('Email already exist. Please login using your existing account.')

        self.errors.append(self.username)
        self.errors.append(self.email)
        self.errors.append(self.password)

        # if len(password) < 8 or len(password) > 50:
        #     self.errors.append('Password must be between 8 and 50 characters')

        # if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", password):
        #     self.errors.append('Password must contain at least one uppercase letter, one lowercase letter and one special character')



