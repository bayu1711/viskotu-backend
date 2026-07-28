from rest_framework import serializers
from .models import Campaign, CreativeAsset, CampaignObjective, TargetingRegion, TargetingMethod
from apps.users.serializers import UserSerializer


class CampaignObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignObjective
        fields = ['id', 'code', 'label', 'tag', 'description', 'order']


class TargetingRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingRegion
        fields = ['id', 'code', 'name', 'impressions', 'order']


class TargetingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetingMethod
        fields = ['id', 'code', 'label', 'description', 'order']


class CreativeAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = CreativeAsset
        fields = [
            'id', 'campaign', 'name', 'file', 'file_url', 'thumbnail',
            'thumbnail_url', 'asset_type', 'file_size', 'dimensions',
            'created_at',
        ]
        read_only_fields = ['id', 'advertiser', 'created_at', 'file_url', 'thumbnail_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class AdminCreativeAssetSerializer(CreativeAssetSerializer):
    advertiser = UserSerializer(read_only=True)

    class Meta(CreativeAssetSerializer.Meta):
        fields = CreativeAssetSerializer.Meta.fields + ['advertiser']


class CampaignSerializer(serializers.ModelSerializer):
    advertiser = UserSerializer(read_only=True)
    assets = CreativeAssetSerializer(many=True, read_only=True)
    ctr = serializers.FloatField(read_only=True)
    objective_detail = CampaignObjectiveSerializer(source='objective', read_only=True)
    # Accept objective as a code string when writing
    objective = serializers.SlugRelatedField(
        slug_field='code',
        queryset=CampaignObjective.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Campaign
        fields = [
            'id', 'advertiser', 'name', 'objective', 'objective_detail', 'status',
            'budget', 'spend', 'impressions', 'clicks', 'ctr', 'conversions',
            'start_date', 'end_date', 'target_locations', 'target_audience',
            'assets', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'advertiser', 'spend', 'impressions', 'clicks', 'conversions', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['advertiser'] = self.context['request'].user
        return super().create(validated_data)


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight for dashboard list view."""
    ctr = serializers.FloatField(read_only=True)
    objective_detail = CampaignObjectiveSerializer(source='objective', read_only=True)
    objective = serializers.SlugRelatedField(
        slug_field='code',
        queryset=CampaignObjective.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'objective', 'objective_detail', 'status',
            'budget', 'spend', 'impressions', 'clicks', 'ctr',
            'start_date', 'end_date', 'created_at',
        ]
