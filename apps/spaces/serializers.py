from rest_framework import serializers
from .models import Space, SpacePhoto, SpaceAvailability
from apps.users.serializers import UserSerializer
from apps.core.models import Category

def resolve_category_to_choice(category_val):
    from apps.spaces.models import Space
    valid_choices = [c[0] for c in Space.CATEGORY_CHOICES]
    if not category_val:
        return valid_choices[0]
    
    category_str = str(category_val).strip().lower()
    if category_str in valid_choices:
        return category_str
        
    try:
        category_obj = Category.objects.filter(id=category_val).first() or Category.objects.filter(name__iexact=category_val).first()
        if category_obj:
            name = category_obj.name.lower()
            if 'vehicle' in name:
                return 'vehicles'
            elif 'real estate' in name or 'retail' in name:
                return 'fixed'
            elif 'electronic' in name or 'gadget' in name or 'accessor' in name:
                return 'gadgets'
            elif 'apparel' in name or 'wearable' in name:
                return 'wearables'
            elif 'pet' in name or 'animal' in name:
                return 'animals'
            elif 'sport' in name or 'event' in name:
                return 'events'
    except Exception:
        pass
    
    return valid_choices[0]

def resolve_choice_to_category_id(choice_val):
    if not choice_val:
        return None
    choice_str = str(choice_val).strip().lower()
    
    name_pattern = None
    if choice_str == 'vehicles':
        name_pattern = 'Vehicles'
    elif choice_str == 'fixed':
        name_pattern = 'Real Estate'
    elif choice_str == 'gadgets':
        name_pattern = 'Electronics'
    elif choice_str == 'wearables':
        name_pattern = 'Apparel'
    elif choice_str == 'animals':
        name_pattern = 'Pets'
    elif choice_str == 'events':
        name_pattern = 'Sports'
        
    if name_pattern:
        cat = Category.objects.filter(name__iexact=name_pattern).first()
        if cat:
            return str(cat.id)
            
    try:
        cat = Category.objects.filter(id=choice_val).first()
        if cat:
            return str(cat.id)
    except Exception:
        pass
        
    cat = Category.objects.all().first()
    return str(cat.id) if cat else None


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

    class Meta:
        model = Space
        fields = [
            'id', 'owner', 'name', 'description', 'category', 'category_label', 'item_type',
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

    def get_category(self, obj):
        """Return the internal choice value (e.g. 'fixed', 'vehicles')"""
        return obj.category

    def get_category_label(self, obj):
        """Return human-readable label for the category"""
        for choice_val, label in Space.CATEGORY_CHOICES:
            if obj.category == choice_val:
                return label
        return obj.category.replace('_', ' ').title() if obj.category else ''

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class SpaceCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.CharField()

    class Meta:
        model = Space
        exclude = ['owner', 'created_at', 'updated_at']

    def validate_category(self, value):
        return resolve_category_to_choice(value)

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
        return obj.category

    def get_primary_photo(self, obj):
        primary = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if primary:
            request = self.context.get('request')
            url = primary.image.url
            return request.build_absolute_uri(url) if request else url
        return None
