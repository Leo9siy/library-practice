from datetime import timedelta, timezone

from django.core.management import BaseCommand

from Payment.models import Payment


class Command(BaseCommand):
    help = "Mark Stripe sessions as expired if not completed within time window"

    def handle(self, *args, **options):
        expiration_time = timezone.now() - timedelta(hours=1)

        expired = Payment.objects.filter(
            status="PENDING", created_at__lt=expiration_time
        ).update(status="EXPIRED")

        self.stdout.write(self.style.SUCCESS(f"Expired {expired} payment(s)"))
