from django.db import models
from django.utils.timezone import now

from Borrowing.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.PAYMENT,
    )

    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.type} for {self.borrowing.user.email} - {self.status}"

    class Meta:
        ordering = ["-id"]
