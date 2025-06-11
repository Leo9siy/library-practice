from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from Payment.models import Payment
from Borrowing.models import Borrowing
from django.contrib.auth import get_user_model
from Book.models import Book

User = get_user_model()


class PaymentSuccessCancelTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="pass")
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Book", author="Author", cover="HARD", inventory=3, daily_fee=1
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2024-01-01",
            expected_return_date="2024-01-05",
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            money_to_pay=4,
            session_id="test_session_id",
            session_url="https://stripe.com/checkout/test_session_id",
        )

    @patch("Payment.views.stripe.checkout.Session.retrieve")
    def test_payment_success(self, mock_retrieve):
        mock_retrieve.return_value = type("Session", (), {"payment_status": "paid"})()

        url = (
            reverse("Payment:payment-success")
            + f"?session_id={self.payment.session_id}"
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PAID")
        self.assertIn("Payment completed successfully", response.data["message"])

    def test_payment_cancel(self):
        url = reverse("Payment:payment-cancel")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Payment was cancelled", response.data["message"])
