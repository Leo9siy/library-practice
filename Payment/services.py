import stripe
from django.conf import settings
from rest_framework.reverse import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_session(borrowing, amount_cents=None, description=None, request=None):
    success_url = request.build_absolute_uri(
        reverse("Payment:payment-success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("Payment:payment-cancel")
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": description or borrowing.book.title,
                },
                "unit_amount": amount_cents or int(borrowing.book.daily_fee * 100),
            },
            "quantity": (borrowing.expected_return_date - borrowing.borrow_date).days,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return session.url, session.id
