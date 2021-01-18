from models.base_model import BaseModel
from models.user import User
import peewee as pw

class Image(BaseModel):
    user_id = pw.ForeignKeyField(User, backref='images')
    photo_url = pw.CharField()