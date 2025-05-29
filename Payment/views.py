import stripe
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from Payment.models import Payment
from Payment.serializers import PaymentSerializer, PaymentDetailSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("borrowing__user", "borrowing__book").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]

        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not (user.is_staff or user.is_superuser):
            queryset = queryset.filter(borrowing__user=user)

        payment_type = self.request.query_params.get("type")
        if payment_type:
            queryset = queryset.filter(type=payment_type.upper())

        payment_status = self.request.query_params.get("status")
        if payment_status:
            queryset = queryset.filter(status=payment_status.upper())

        return queryset


class PaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "session_id is required"}, status=400)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError:
            return Response({"error": "Invalid session ID"}, status=400)

        if session.payment_status == "paid":
            payment = get_object_or_404(Payment, session_id=session_id)
            payment.status = "PAID"
            payment.save()
            return Response({"message": "Payment completed successfully!"})

        return Response({"message": "Payment is not completed."}, status=400)


class PaymentCancelView(APIView):
    def get(self, request):
        return Response({"message": "Payment was cancelled. You can retry later."})

