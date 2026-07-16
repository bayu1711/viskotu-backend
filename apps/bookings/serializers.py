from rest_framework import serializers
from .models import Booking
from apps.spaces.serializers import SpaceSerializer
from apps.campaigns.serializers import CampaignSerializer
from apps.users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    space_detail = SpaceSerializer(source='space', read_only=True)
    advertiser_detail = UserSerializer(source='advertiser', read_only=True)
    campaign_detail = CampaignSerializer(source='campaign', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'advertiser', 'space', 'space_detail', 'advertiser_detail', 'campaign', 'campaign_detail',
            'status', 'start_date', 'end_date', 'total_price', 'platform_fee',
            'paid_at', 'cancelled_at', 'cancel_reason', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'advertiser', 'platform_fee', 'paid_at', 'cancelled_at', 'created_at', 'updated_at']
