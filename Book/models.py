from django.db import models


class Book(models.Model):
    class CoverChoise(models.TextChoices):
        HARD = "HARD", "Hardcover"
        SOFT = "SOFT", "Softcover"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    cover = models.CharField(
        max_length=100, choices=CoverChoise.choices, default=CoverChoise.SOFT
    )
    inventory = models.PositiveIntegerField()

    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
