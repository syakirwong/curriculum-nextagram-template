from models.base_model import BaseModel
from werkzeug.security import generate_password_hash
from flask_login import UserMixin, current_user
from playhouse.hybrid import hybrid_property
import peewee as pw
import re


class User(UserMixin, BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(index=True, unique=True)
    password= pw.CharField(null=False)
    password_nohash = None
    profile_picture = pw.CharField(default='null')
    is_private = pw.BooleanField(default=False)

    @hybrid_property
    def full_image_path(self):
        if self.profile_picture:
            from app import app
            return app.config.get("AWS_DOMAIN") + self.profile_picture
        else:
            return ""

    def follow_status(self, following):
        from models.follow import Follow
        return Follow.get_or_none(Follow.follower==self.id, Follow.following==following.id)

    def follow(self, following):
            from models.follow import Follow
            if Follow.get_or_none(Follow.follower == self.id, Follow.following == following.id):
                return False
            else:
                if following.is_private:
                    Follow.create(follower = self.id, following=following.id, is_approved=False)
                else:
                    Follow.create(follower=self.id, following=following.id, is_approved=True)

                return True

    def unfollow(self, following):
        from models.follow import Follow
        Follow.delete().where(self.id == Follow.follower and following == Follow.following).execute()
        return True

    @hybrid_property
    def followers(self):
        from models.follow import Follow
        # followers = (
        #     User.select()
        #     .join(Follow, on=(User.id == Follow.follower_id))
        #     .where(
        #         Follow.following == self.id,
        #         Follow.is_approved==True
        # ))
        followers = Follow.select().where(Follow.following == self.id, Follow.is_approved==True)

        followers_list = []
        for follower in followers:
            followers_list.append(follower)
        return followers_list

    @hybrid_property
    def followings(self):
        from models.follow import Follow

        followings = (
            User.select()
            .join(Follow, on=(User.id == Follow.following_id))
            .where(
                Follow.follower == self.id,
                Follow.is_approved==True
        ))

        # followings = Follow.select().where(Follow.follower == self.id, Follow.is_approved==True)

        followings_list = []
        for following in followings:
            followings_list.append(following)
        return followings_list

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
