from django.urls import path
from rest_framework.routers import DefaultRouter

from Payment import views

router = DefaultRouter()
router.register("payments", views.PaymentViewSet, basename="payments")

urlpatterns = [
    path("success/", views.PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", views.PaymentCancelView.as_view(), name="payment-cancel"),
] + router.urls

app_name = "Payment"
