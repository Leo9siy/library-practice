import stripe
from django.conf import settings
from rest_framework.reverse import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_session(
    borrowing,
    request,
    amount,
    success_url=None,
    cancel_url=None,
    description="",
    payment_type="PAYMENT",
):
    if not success_url:
        success_url = request.build_absolute_uri(reverse("Payment:payment-success"))
    if not cancel_url:
        cancel_url = request.build_absolute_uri(reverse("Payment:payment-cancel"))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(amount * 100),  # cents
                    "product_data": {
                        "name": f"{payment_type.title()} for: {borrowing.book.title}",
                        "description": description,
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "borrowing_id": str(borrowing.id),
            "type": payment_type
        }
    )

    return session.url, session.id