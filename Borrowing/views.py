from datetime import datetime

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from Borrowing.models import Borrowing
from Borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer, ReturnBorrowingSerializer


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
        if self.action in ["create", "list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.select_related("user", "book").all()

        user_id = self.request.query_params.get("user_id")
        if user.is_staff or user.is_superuser:
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=user)


        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset


    @action(detail=True, methods=["POST", "GET"], url_path="return", permission_classes=[permissions.IsAuthenticated])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if self.action == "GET":
            if request.method == "GET":
                if borrowing.actual_return_date:
                    return Response(
                        {"detail": "Book already returned"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {"detail": "You can return the book"},
                    status=status.HTTP_200_OK
                )

        serializer = ReturnBorrowingSerializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
