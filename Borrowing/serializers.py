from datetime import date, timedelta

from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from Borrowing.models import Borrowing
from Payment.models import Payment
from Payment.serializers import PaymentSerializer
from Payment.services import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]
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

        user = self.context["request"].user
        has_pending = user.borrowings.filter(
            payments__status="PENDING",
            user=user,
        ).exists()

        if has_pending:
            raise serializers.ValidationError(
                {"non_field_errors": ["Unpaid payments detected."]}
            )

        book = data["book"]

        if book.inventory <= 0:
            raise serializers.ValidationError({"book": "Book is not available."})

        if "expected_return_date" not in data:
            data["expected_return_date"] = date.today() + timedelta(days=60)

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        book = validated_data["book"]
        borrowing = super().create(validated_data)

        with transaction.atomic():

            book.inventory -= 1
            book.save()

            money_to_pay = (
                validated_data["expected_return_date"] - borrowing.borrow_date
            ).days * borrowing.book.daily_fee

            session_url, session_id = create_stripe_session(
                borrowing,
                request=request,
                amount=money_to_pay,
                description=f"Payment for: {book.title}",
                payment_type="PAYMENT",
            )

            Payment.objects.create(
                borrowing=borrowing,
                status="PENDING",
                type="PAYMENT",
                session_url=session_url,
                session_id=session_id,
                money_to_pay=money_to_pay,
            )

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
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
        ]


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
        today = date.today()

        with transaction.atomic():

            instance.actual_return_date = today
            instance.book.inventory += 1
            instance.book.save()
            instance.save()

            if today > instance.expected_return_date:
                payment = instance.payments.filter(type="PAYMENT", status="PAID").first()
                if not payment:
                    payment = instance.payments.filter(type="PAYMENT", status="PENDING").first()

                if payment:
                    overdue_days = (today - instance.expected_return_date).days
                    fine_amount = (
                        overdue_days * instance.book.daily_fee * settings.FINE_MULTIPLIER
                    )

                    session_url, session_id = create_stripe_session(
                        instance,
                        request=self.context["request"],
                        amount=fine_amount,
                        description=f"Fine for '{instance.book.title}' - {overdue_days} days overdue",
                        payment_type="FINE",
                    )

                    payment.type = "FINE"
                    payment.status = "PENDING"
                    payment.money_to_pay = fine_amount
                    payment.session_url = session_url
                    payment.session_id = session_id
                    payment.save()

        return instance
