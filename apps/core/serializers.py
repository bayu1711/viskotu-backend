from rest_framework import serializers
from .models import SiteSettings, SupportTicket, SLAEvent


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['privacy_policy', 'terms_of_service', 'updated_at']
        read_only_fields = ['updated_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = '__all__'

class SLAEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAEvent
        fields = '__all__'
