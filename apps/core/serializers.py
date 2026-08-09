from rest_framework import serializers
from .models import SiteSettings, SupportTicket, SLAEvent, Category, ItemType, SurfaceMaterial, PointOfInterest, UsageType, PrintResolution, AudienceBehavior, TrafficDensity, PeakExposure


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


class CategorySerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'image', 'isActive', 'sortOrder']


class ItemTypeSerializer(serializers.ModelSerializer):
    categoryId = serializers.UUIDField(source='category.id', read_only=True)
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = ItemType
        fields = ['id', 'name', 'categoryId', 'description', 'isActive', 'sortOrder']


class SurfaceMaterialSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = SurfaceMaterial
        fields = ['id', 'name', 'description', 'isActive', 'sortOrder']

class UsageTypeSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = UsageType
        fields = ['id', 'value', 'label', 'isActive', 'sortOrder']

class PrintResolutionSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = PrintResolution
        fields = ['id', 'value', 'label', 'isActive', 'sortOrder']

class AudienceBehaviorSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = AudienceBehavior
        fields = ['id', 'value', 'label', 'isActive', 'sortOrder']

class TrafficDensitySerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = TrafficDensity
        fields = ['id', 'value', 'label', 'isActive', 'sortOrder']

class PeakExposureSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source='is_active', read_only=True)
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = PeakExposure
        fields = ['id', 'value', 'label', 'isActive', 'sortOrder']

class PointOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfInterest
        fields = ['id', 'name', 'category', 'lat', 'lng']
