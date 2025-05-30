from datetime import timedelta, date

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Book.models import Book
from Borrowing.models import Borrowing
from Payment.models import Payment


class BorrowingTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="pass"
        )
        self.book = Book.objects.create(title="Test Book", inventory=5, daily_fee=10)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_borrowing_creates_payment(self):
        expected_return = date.today() + timedelta(days=7)
        response = self.client.post(
            reverse("Borrowing:borrowing-list"),
            {"book": self.book.id, "expected_return_date": expected_return.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        borrowing = Borrowing.objects.first()

        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book.inventory, 4)

        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        self.assertEqual(payment.borrowing, borrowing)
        self.assertEqual(payment.status, "PENDING")
        self.assertEqual(payment.type, "PAYMENT")
        self.assertGreater(len(payment.session_url), 10)


def test_return_borrowing_with_fine_creates_payment(self):
    borrow_date = date.today() - timedelta(days=10)
    expected_return_date = date.today() - timedelta(days=5)

    borrowing = Borrowing.objects.create(
        user=self.user,
        book=self.book,
        borrow_date=borrow_date,
        expected_return_date=expected_return_date,
    )

    url = reverse("Borrowing:borrowing-return-book", kwargs={"pk": borrowing.id})
    response = self.client.post(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    borrowing.refresh_from_db()
    self.assertIsNotNone(borrowing.actual_return_date)
    self.assertEqual(borrowing.book.inventory, 6)

    fines = Payment.objects.filter(borrowing=borrowing, type="FINE")
    self.assertEqual(fines.count(), 1)
    self.assertEqual(fines.first().status, "PENDING")


def test_return_borrowing_without_fine(self):
    expected_return = date.today() + timedelta(days=2)
    borrowing = Borrowing.objects.create(
        user=self.user,
        book=self.book,
        borrow_date=date.today(),
        expected_return_date=expected_return,
    )

    url = reverse("Borrowing:borrowing-return-book", kwargs={"pk": borrowing.id})
    response = self.client.post(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    borrowing.refresh_from_db()
    self.assertIsNotNone(borrowing.actual_return_date)
    self.assertEqual(borrowing.book.inventory, 6)

    fines = Payment.objects.filter(borrowing=borrowing, type="FINE")
    self.assertEqual(fines.count(), 0)


def test_double_return_should_fail(self):
    borrowing = Borrowing.objects.create(
        user=self.user,
        book=self.book,
        borrow_date=date.today() - timedelta(days=10),
        expected_return_date=date.today() - timedelta(days=5),
        actual_return_date=date.today(),  # уже возвращена
    )

    url = reverse("Borrowing:borrowing-return-book", kwargs={"pk": borrowing.id})
    response = self.client.post(url)

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("already returned", response.data["non_field_errors"][0].lower())


def test_borrowing_not_allowed_when_inventory_zero(self):
    self.book.inventory = 0
    self.book.save()

    expected_return = date.today() + timedelta(days=7)
    response = self.client.post(
        reverse("Borrowing:borrowing-list"),
        {"book": self.book.id, "expected_return_date": expected_return.isoformat()},
    )

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("not available", response.data["non_field_errors"][0].lower())


def test_expected_return_date_cannot_be_in_past(self):
    expected_return = date.today() - timedelta(days=1)
    response = self.client.post(
        reverse("Borrowing:borrowing-list"),
        {"book": self.book.id, "expected_return_date": expected_return.isoformat()},
    )

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn("cannot be in past", str(response.data))
