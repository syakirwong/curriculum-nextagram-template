import os
import braintree
from flask import Blueprint, render_template, request
from models.image import Image

AWS_DOMAIN = 'http://{}.s3-ap-southeast-1.amazonaws.com/'.format(os.getenv('AWS_BUCKET'))

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
    return render_template('images/image.html', domain=AWS_DOMAIN, image=image, token=token)

@images_blueprint.route("/receive_payment", methods=["POST"])
def pay():
    nonce = request.form["nonce"]
    print("ITSSSSSS HEREEEEEEEEEEEEEE ====> " + nonce)
    result = gateway.transaction.sale({
        "amount": "100.00",
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })
    if result.is_success:
        return "Payment Received"
    else:
        return "Payment Failed"