from datetime import date, timedelta

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from Book.models import Book
from Borrowing.models import Borrowing
from django.contrib.auth import get_user_model

from Payment.models import Payment

User = get_user_model()

class BorrowingCreateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="pass1234"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=1,
            daily_fee=1.5
        )

        self.url = reverse("Borrowing:borrowing-list")

    def test_borrowing_fails_if_no_inventory(self):
        self.book.inventory = 0
        self.book.save()

        data = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7)
        }
        response = self.client.post(reverse("Borrowing:borrowing-list"), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Book is not available", str(response.data))
        self.assertEqual(Borrowing.objects.count(), 0)

    def test_cannot_borrow_with_pending_payments(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=5)
        )
        Payment.objects.create(
            borrowing=borrowing,
            status="PENDING",
            type="PAYMENT",
            session_url="http://example.com",
            session_id="test123",
            money_to_pay=50,
        )

        data = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=5))
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("unpaid payments", str(response.data).lower())