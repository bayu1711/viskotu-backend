from rest_framework import serializers
from .models import PrintJob
from apps.bookings.serializers import BookingSerializer
from apps.users.serializers import UserSerializer

class PrintJobSerializer(serializers.ModelSerializer):
    booking_detail = BookingSerializer(source='booking', read_only=True)
    printer_detail = UserSerializer(source='printer', read_only=True)

    class Meta:
        model = PrintJob
        fields = [
            'id', 'booking', 'booking_detail', 'printer', 'printer_detail',
            'status', 'priority', 'printer_source', 'material', 'size',
            'quantity', 'finish', 'checklist', 'deadline', 'accept_deadline',
            'accepted_at', 'completed_at', 'reroute_count', 'tried_printer_ids',
            'proof_file', 'proof_submitted_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
