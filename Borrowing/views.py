from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from Borrowing.models import Borrowing
from Borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    ReturnBorrowingSerializer,
)

from Borrowing.telegram_send import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingDetailSerializer

        if self.action == "return_book":
            return ReturnBorrowingSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve", "return_book"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.select_related("user", "book").all()

        if not (user.is_superuser or user.is_staff):
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        if user_id and (user.is_staff or user.is_superuser):
            queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            is_active = is_active.lower()

            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="True — active (not returned) borrowings; False — returned.",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="(Only admins) Users borrowings.",
            ),
        ],
        responses={
            200: BorrowingSerializer(many=True)
        },
        description="Take a Borrowings list, Admin can filter by id.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=BorrowingSerializer,
        responses={201: BorrowingDetailSerializer},
        description="Create borrowing. Get down amount in inventory and created payment in strip.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        methods=["GET"],
        description="Check if the book can be returned.",
        responses={
            200: OpenApiResponse(description="Book can be returned"),
            400: OpenApiResponse(description="Book already returned"),
            403: OpenApiResponse(description="Access denied"),
        },
    )
    @extend_schema(
        methods=["POST"],
        description="Return a borrowed book. Sets actual return date, increases inventory. Creates a fine if overdue.",
        responses={
            200: ReturnBorrowingSerializer,
            400: OpenApiResponse(description="Book already returned or invalid data"),
            403: OpenApiResponse(
                description="Only the borrower or admin can return the book."
            ),
        },
    )
    @action(
        detail=True,
        methods=["POST", "GET"],
        url_path="return",
        permission_classes=[permissions.IsAuthenticated],
    )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to return this borrowing."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "GET":
            if borrowing.actual_return_date:
                return Response(
                    {"detail": "Book already returned"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": "You can return the book"}, status=status.HTTP_200_OK
            )

        serializer = ReturnBorrowingSerializer(
            borrowing,
            data=request.data,
            context={"request": request},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_telegram_message(
            f"📚 {borrowing.user.email} returned book: {borrowing.book.title}\n"
            f"🕓 Returns date: {datetime.today().strftime('%Y-%m-%d')}"
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
