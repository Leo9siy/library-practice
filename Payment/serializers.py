from rest_framework import serializers


from Payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        ]
        read_only_fields = ["id", "session_url", "session_id", "money_to_pay"]


class PaymentDetailSerializer(PaymentSerializer):
    def __init__(self, *args, **kwargs):
        from Borrowing.serializers import BorrowingSerializer

        self.fields["borrowing"] = BorrowingSerializer(read_only=True)
        super().__init__(*args, **kwargs)
