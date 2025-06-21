import stripe
from django.conf import settings
import os

stripe.api_key = settings.STRIPE_SECRET_KEY

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

success_url = f'{FRONTEND_URL}/user-profile?result=success'
cancel_url = f'{FRONTEND_URL}/user-profile?result=fail'


def create_checkout_session(payment_id, book):

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': book.price,
                        'product_data': {
                            'name': book.name,
                            'images': ["https://backend.mapyourfreedom.com/media/product_images/myf.png"]
                        },
                    },
                    'quantity': 1
                },
            ],
            mode='payment',
            success_url=success_url,  # <-- Localhost for success
            cancel_url=cancel_url,      # <-- Localhost for cancel
            client_reference_id=payment_id
        )
        return checkout_session
    
    except Exception as error:
        print(error)
        return None


