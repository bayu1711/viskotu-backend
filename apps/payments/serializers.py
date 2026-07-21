from rest_framework import serializers
from .models import Payment, Payout
from apps.placements.serializers import AdPlacementSerializer

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'payer', 'created_at', 'updated_at']

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = '__all__'
        read_only_fields = ['id', 'recipient', 'created_at', 'updated_at']
