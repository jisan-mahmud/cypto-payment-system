from rest_framework import serializers

class PaymentVerifySerializer(serializers.Serializer):
    network = serializers.ChoiceField(choices=["polygon", "solana"])
    wallet = serializers.CharField(required=False, allow_blank=True)
    tx_hash = serializers.CharField()
