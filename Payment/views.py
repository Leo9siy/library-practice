import stripe
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from Borrowing.telegram_send import send_telegram_message
from Payment.models import Payment
from Payment.serializers import PaymentSerializer, PaymentDetailSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related(
        "borrowing__user", "borrowing__book"
    ).all()
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
        queryset = self.queryset
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by Type: PAYMENT or FINE",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter by Status: PENDING or PAID",
            ),
        ],
        responses={200: PaymentSerializer(many=True)},
        description="Take payments list. Users by theiself and Admins all. Can filter by Type and Status.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={200: PaymentDetailSerializer},
        description="Take Payment detail by Id. Access only for admins.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class PaymentSuccessView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="session_id",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={
            200: OpenApiResponse(description="Payment confirmed successfully"),
            400: OpenApiResponse(description="Invalid or unpaid session"),
        },
        description="Confirm Stripe payment success via session_id query parameter.",
    )
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
            if payment.status != "PAID":
                payment.status = "PAID"
                payment.save()

                send_telegram_message(
                    f"✅ Оплата прошла успешно\n"
                    f"👤 {payment.borrowing.user.email}\n"
                    f"📘 {payment.borrowing.book.title}\n"
                    f"💰 ${payment.money_to_pay} ({payment.type})"
                )

            return Response({"message": "Payment completed successfully!"})

        return Response({"message": "Payment is not completed."}, status=400)


class PaymentCancelView(APIView):
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Payment was cancelled. Can retry.")
        },
        description="Stripe cancel redirect. Informs user that payment failed or was cancelled.",
    )
    def get(self, request):
        return Response({"message": "Payment was cancelled. You can retry later."})
