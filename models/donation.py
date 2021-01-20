from models.base_model import BaseModel
from models.user import User
from models.image import Image
import peewee as pw

class Donation(BaseModel):
    braintree_nonce = pw.CharField()
    amount = pw.CharField()
    image_id = pw.ForeignKeyField(Image, backref='donations')
    by_user_id = pw.ForeignKeyField(User, backref='donations')
    to_user_id = pw.ForeignKeyField(User, backref='donations')