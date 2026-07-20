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

    def validate(self, data):
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = data.get('end_date', getattr(self.instance, 'end_date', None))
        space = data.get('space', getattr(self.instance, 'space', None))
        status = data.get('status', getattr(self.instance, 'status', 'pending'))

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({"end_date": "End date must be after or equal to start date."})

        if space and start_date and end_date and status not in ['cancelled', 'disputed']:
            from apps.spaces.models import SpaceAvailability

            # Check existing overlapping bookings
            overlapping = Booking.objects.filter(
                space=space,
                status__in=['pending', 'confirmed', 'paid', 'completed'],
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({"detail": "Space is already booked for overlapping dates."})

            # Check SpaceAvailability blocked dates
            blocked = SpaceAvailability.objects.filter(
                space=space,
                is_blocked=True,
                date__range=[start_date, end_date]
            )
            if blocked.exists():
                raise serializers.ValidationError({"detail": "Space is unavailable or blocked on one or more dates in the selected range."})

        return data
