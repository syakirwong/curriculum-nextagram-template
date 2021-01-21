from models.base_model import BaseModel
from models.user import User
from models.image import Image
import peewee as pw

class Donation(BaseModel):
    amount = pw.DecimalField()
    image_id = pw.ForeignKeyField(Image, backref='donations')
    sender = pw.ForeignKeyField(User, backref='donations')
