from rest_framework import serializers
from .models import Space, SpacePhoto, SpaceAvailability
from apps.users.serializers import UserSerializer
from apps.core.models import Category, ItemType, SurfaceMaterial, UsageType, PrintResolution, AudienceBehavior, TrafficDensity, PeakExposure


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
    category = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    item_type_label = serializers.SerializerMethodField()
    usage_type_label = serializers.SerializerMethodField()
    material_label = serializers.SerializerMethodField()
    min_dpi_label = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            'id', 'owner', 'name', 'description', 'category', 'category_label', 'quantity', 'item_type', 'item_type_label', 'usage_type', 'usage_type_label',
            'address', 'city', 'state', 'zip_code', 'latitude', 'longitude',
            'end_point', 'primary_roads', 'service_radius', 'facing_direction',
            'width', 'height', 'material', 'material_label', 'min_dpi', 'min_dpi_label', 'accepted_formats',
            'orientation', 'physical_shape', 'reference_photo', 'designer_notes',
            'base_rate', 'billing_period', 'custom_period_days', 'min_placement_duration',
            'bulk_discount_enabled', 'bulk_discount_percentage',
            'fulfillment_type', 'self_fulfillment_reason',
            'print_partner_routing', 'preferred_production_partner',
            'proof_of_play_method', 'install_lead_days', 'production_lead_days',
            'status', 'is_featured', 'occupancy_rate',
            'impressions_estimate', 'audience_behaviors', 'traffic_densities', 'peak_exposures',
            'photos', 'primary_photo',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_category(self, obj):
        """Return the ID of the category"""
        return str(obj.category.id) if obj.category else None

    def get_category_label(self, obj):
        """Return human-readable label for the category"""
        return obj.category.name if obj.category else ''

    def get_item_type_label(self, obj):
        return obj.item_type.name if obj.item_type else None

    def get_usage_type_label(self, obj):
        return obj.usage_type.label if obj.usage_type else None

    def get_material_label(self, obj):
        return obj.material.name if obj.material else None

    def get_min_dpi_label(self, obj):
        return obj.min_dpi.label if obj.min_dpi else None

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class SpaceCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    item_type = serializers.PrimaryKeyRelatedField(queryset=ItemType.objects.all(), required=False, allow_null=True)
    usage_type = serializers.PrimaryKeyRelatedField(queryset=UsageType.objects.all(), required=False, allow_null=True)
    material = serializers.PrimaryKeyRelatedField(queryset=SurfaceMaterial.objects.all(), required=False, allow_null=True)
    min_dpi = serializers.PrimaryKeyRelatedField(queryset=PrintResolution.objects.all(), required=False, allow_null=True)
    
    audience_behaviors = serializers.PrimaryKeyRelatedField(queryset=AudienceBehavior.objects.all(), many=True, required=False)
    traffic_densities = serializers.PrimaryKeyRelatedField(queryset=TrafficDensity.objects.all(), many=True, required=False)
    peak_exposures = serializers.PrimaryKeyRelatedField(queryset=PeakExposure.objects.all(), many=True, required=False)

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
    category = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            'id', 'name', 'category', 'city', 'state',
            'latitude', 'longitude', 'base_rate', 'billing_period',
            'impressions_estimate', 'status', 'is_featured',
            'primary_photo', 'owner_name',
        ]

    def get_category(self, obj):
        return str(obj.category.id) if obj.category else None

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None
