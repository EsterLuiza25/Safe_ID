from rest_framework import serializers

from .models import Transaction


class TransactionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "customer_id",
            "ip_address",
            "device_fingerprint",
            "risk_score",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "ip_address", "risk_score", "status", "created_at"]


class TransactionSerializer(serializers.ModelSerializer):
    risk_reasons = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        required=False,
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "customer_id",
            "ip_address",
            "device_fingerprint",
            "risk_score",
            "status",
            "created_at",
            "risk_reasons",
        ]
        read_only_fields = ["id", "ip_address", "risk_score", "status", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor da transacao deve ser maior que zero.")
        return value

    def validate_customer_id(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("customer_id nao pode ser vazio.")
        return value

    def validate_device_fingerprint(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("device_fingerprint nao pode ser vazio.")
        return value


class AuthorizeTransactionRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    customer_id = serializers.CharField(max_length=64)
    device_fingerprint = serializers.CharField(max_length=255)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor da transacao deve ser maior que zero.")
        return value

    def validate_customer_id(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("customer_id nao pode ser vazio.")
        return value

    def validate_device_fingerprint(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("device_fingerprint nao pode ser vazio.")
        return value
