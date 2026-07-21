from rest_framework import serializers
from .models import PrintJob
from apps.bookings.serializers import BookingSerializer
from apps.users.serializers import UserSerializer

class PrintJobSerializer(serializers.ModelSerializer):
    booking_detail = BookingSerializer(source='booking', read_only=True)
    production_partner_detail = UserSerializer(source='production_partner', read_only=True)

    class Meta:
        model = PrintJob
        fields = [
            'id', 'booking', 'booking_detail', 'production_partner', 'production_partner_detail',
            'status', 'priority', 'production_partner_source', 'material', 'size',
            'quantity', 'finish', 'checklist', 'deadline', 'accept_deadline',
            'accepted_at', 'completed_at', 'reroute_count', 'tried_production_partner_ids',
            'proof_file', 'proof_submitted_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
