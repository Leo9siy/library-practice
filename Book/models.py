from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext as _


class Book(models.Model):
    class CoverChoise(models.TextChoices):
        HARD = 'HARD', "Hardcover"
        SOFT = 'SOFT', "Softcover"


    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    cover = models.CharField(max_length=100, choices=CoverChoise.choices, default=CoverChoise.SOFT)
    inventory = models.PositiveIntegerField()

    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

# class Payment(models.Model):
#     class StatusChoise(models.TextChoices):
#         PENDING = 'PENDING', _('Pending')
#         PAID = 'PAID', _('Paid')
#
#     class TypeChoise(models.TextChoices):
#         PAYMENT = 'PAYMENT', _('Payment')
#         FINE = 'FINE', _('Fine')
#
#     borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='payments')
#     session_url = models.URLField()
#     session_id = models.CharField(max_length=100)
#     money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
