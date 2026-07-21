from rest_framework import serializers
from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['privacy_policy', 'terms_of_service', 'updated_at']
        read_only_fields = ['updated_at']
