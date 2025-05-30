from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from Book.models import Book
from Borrowing.models import Borrowing
from Payment.models import Payment


class PaymentViewSetTestCase(TestCase):
    def setUp(self):
        Payment.objects.all().delete()
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(title="Test Book", inventory=10, daily_fee=10)

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=5),
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            money_to_pay=100,
            session_url="https://stripe.com/test",
            session_id="sess_test",
        )

    def test_user_sees_only_own_payments(self):
        other_user = get_user_model().objects.create_user(
            email="other@test.com", password="otherpass"
        )
        other_borrowing = Borrowing.objects.create(
            user=other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        Payment.objects.create(
            borrowing=other_borrowing, status="PAID", type="FINE", money_to_pay=55
        )

        response = self.client.get(reverse("Payment:payments-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["borrowing"], self.borrowing.id)

    def test_filter_payments_by_type(self):
        Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="FINE",
            money_to_pay=50,
            session_url="https://stripe.com/fine",
            session_id="sess_fine",
        )

        response = self.client.get(reverse("Payment:payments-list") + "?type=FINE")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "FINE")

    def test_filter_payments_by_status(self):
        Payment.objects.create(
            borrowing=self.borrowing,
            status="PAID",
            type="FINE",
            money_to_pay=50,
            session_url="https://stripe.com/paid",
            session_id="sess_paid",
        )

        response = self.client.get(reverse("Payment:payments-list") + "?status=PAID")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "PAID")

    def test_admin_sees_all_payments(self):
        other_user = get_user_model().objects.create_user(
            email="admin2@test.com", password="adminpass"
        )
        other_borrowing = Borrowing.objects.create(
            user=other_user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )
        Payment.objects.create(
            borrowing=other_borrowing, status="PAID", type="FINE", money_to_pay=77
        )

        self.user.is_staff = True
        self.user.save()

        response = self.client.get(reverse("Payment:payments-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_return_book_success(self):
        # Создаём бронирование
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=7),
        )

        # Фиксируем изначальное количество книг на складе
        initial_inventory = self.book.inventory

        # Выполняем POST-запрос на возврат книги
        url = reverse("Borrowing:borrowing-return-book", args=[borrowing.id])
        response = self.client.post(url)

        # Проверки
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Обновляем объекты из базы
        borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, initial_inventory + 1)

    def test_return_book_with_pending_fine_is_blocked(self):
        # Возвращаем книгу с просрочкой
        self.borrowing.expected_return_date = date.today() - timedelta(days=5)
        self.borrowing.save()

        # Создаём штраф вручную
        Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="FINE",
            session_url="https://fake-stripe.com/session",
            session_id="fake_session_id",
            money_to_pay=100.0,
        )

        url = reverse("Borrowing:borrowing-return-book", args=[self.borrowing.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot return book", str(response.data))
