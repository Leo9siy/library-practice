from datetime import date, timedelta

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from Borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ["id", "book", "borrow_date", "expected_return_date", "actual_return_date"]
        read_only_fields = ["id", "borrow_date", "actual_return_date"]


    def validate_expected_return_date(self, value):
        today = date.today()
        max_date = today + timedelta(days=60)
        if value > max_date:
            raise serializers.ValidationError("Max return date is 60 days from today.")
        if value < today:
            raise serializers.ValidationError("Return date cannot be in past.")

        return value


    def validate(self, data):
        book = data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is not available.")

        if "expected_return_date" not in data:
            data["expected_return_date"] = date.today() + timedelta(days=14)

        return data

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        borrowing = Borrowing.objects.create(**validated_data)
        return borrowing


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="email",
        read_only=True,
    )
    book = SlugRelatedField(
        slug_field="title",
        read_only=True,
    )

    class Meta:
        model = Borrowing
        fields = ["id", "user", "book", "borrow_date", "expected_return_date", "actual_return_date"]


class ReturnBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["expected_return_date"]
        read_only_fields = ["expected_return_date"]

    def validate(self, attrs):
        if self.instance.actual_return_date:
            raise serializers.ValidationError("This book is already returned.")
        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = date.today()
        instance.book.inventory += 1
        instance.book.save()
        instance.save()
        return instance
