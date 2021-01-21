import os
import braintree
from flask import Blueprint, render_template, request
from flask_login import current_user
from models.image import Image
from models.user import User
from models.donation import Donation
from app import app
from decimal import Decimal

images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.getenv("BRAINTREE_MERCHANT_ID"),
        public_key=os.getenv("BRAINTREE_PUBLIC_KEY"),
        private_key=os.getenv("BRAINTREE_PRIVATE_KEY")
    )
)

@images_blueprint.route('/<id>', methods=['GET'])
def show(id):
    image = Image.get_by_id(id)
    token = gateway.client_token.generate()
    return render_template('images/image.html', domain=app.config.get('AWS_DOMAIN'), image=image, token=token)

@images_blueprint.route("<id>/receive_payment", methods=["POST"])
def pay(id):
    nonce = request.form["nonce"]
    print(id)
    print("ITSSSSSS HEREEEEEEEEEEEEEE ====> " + nonce)
    result = gateway.transaction.sale({
        "amount": "100.00",
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })
    if result.is_success:
        donation = Donation(sender=User.get_by_id(current_user.id), image_id=id, amount=Decimal(100.00))
        donation.save()
        return "Payment Received"
    else:
        return "Payment Failed"