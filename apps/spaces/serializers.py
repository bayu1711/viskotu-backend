from rest_framework import serializers
from .models import Space, SpacePhoto, SpaceAvailability
from apps.users.serializers import UserSerializer


class SpacePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpacePhoto
        fields = ['id', 'image', 'is_primary', 'order']


class SpaceAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceAvailability
        fields = ['id', 'date', 'is_blocked', 'reason']


class SpaceSerializer(serializers.ModelSerializer):
    photos = SpacePhotoSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    primary_photo = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            'id', 'owner', 'name', 'description', 'category', 'item_type',
            'address', 'city', 'state', 'zip_code', 'latitude', 'longitude',
            'width', 'height', 'material', 'min_dpi', 'accepted_formats',
            'base_rate', 'billing_period', 'min_placement_duration',
            'bulk_discount_enabled', 'bulk_discount_percentage',
            'fulfillment_type', 'self_fulfillment_reason',
            'print_partner_routing', 'preferred_production_partner',
            'install_lead_days', 'production_lead_days',
            'status', 'is_featured', 'occupancy_rate',
            'impressions_estimate', 'photos', 'primary_photo',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class SpaceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        exclude = ['owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class SpaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/browse views."""
    primary_photo = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = Space
        fields = [
            'id', 'name', 'category', 'city', 'state',
            'latitude', 'longitude', 'base_rate', 'billing_period',
            'impressions_estimate', 'status', 'is_featured',
            'primary_photo', 'owner_name',
        ]

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None
