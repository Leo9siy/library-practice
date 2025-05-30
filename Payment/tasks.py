from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from Payment.models import Payment


@shared_task
def expire_old_payments():
    expiration_time = timezone.now() - timedelta(hours=1)
    expired_count = Payment.objects.filter(
        status="PENDING", created_at__lt=expiration_time
    ).update(status="EXPIRED")

    return f"Expired {expired_count} payment(s)"
