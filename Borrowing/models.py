from django.db import models

from Book.models import Book
from User.models import Customer


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='borrowings')
