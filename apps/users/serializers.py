from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import ProductionPartnerProfile, ManagedAccess

User = get_user_model()


class ProductionPartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionPartnerProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    production_partner_profile = ProductionPartnerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'name',
            'role', 'country', 'preferred_currency', 'is_email_verified', 'phone', 'avatar',
            'company_name', 'bio', 'kyc_status', 'created_at',
            'production_partner_profile', 'onboarded_roles',
            'reliability_score',
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'created_at', 'reliability_score']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    country = serializers.CharField(max_length=2, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'role', 'country']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        country = validated_data.get('country')
        currency_map = {'LK': 'LKR', 'US': 'USD', 'GB': 'GBP', 'EU': 'EUR'}
        if country:
            validated_data['preferred_currency'] = currency_map.get(country.upper(), 'USD')
        else:
            validated_data['preferred_currency'] = 'USD'
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangeRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['advertiser', 'space-owner', 'production-partner', 'admin'])


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ManagedAccessSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    owner_email = serializers.SerializerMethodField()
    owner_role = serializers.SerializerMethodField()

    class Meta:
        model = ManagedAccess
        fields = ['id', 'owner', 'managed_user', 'invited_email', 'permissions', 'status', 'created_at', 'name', 'email', 'owner_name', 'owner_email', 'owner_role']
        read_only_fields = ['id', 'owner', 'status', 'created_at']

    def get_name(self, obj):
        if obj.managed_user:
            return obj.managed_user.name
        return ''

    def get_email(self, obj):
        if obj.managed_user:
            return obj.managed_user.email
        return obj.invited_email

    def get_owner_name(self, obj):
        return obj.owner.name

    def get_owner_email(self, obj):
        return obj.owner.email

    def get_owner_role(self, obj):
        return obj.owner.role


class AdminUserSerializer(UserSerializer):
    revenue = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['revenue', 'assets']

    def get_revenue(self, obj):
        from apps.payments.models import Payment, Payout
        from django.db.models import Sum
        if obj.role == 'advertiser':
            return float(Payment.objects.filter(payer=obj, status='succeeded').aggregate(total=Sum('amount'))['total'] or 0)
        else:
            return float(Payout.objects.filter(recipient=obj, status='paid').aggregate(total=Sum('amount'))['total'] or 0)

    def get_assets(self, obj):
        from apps.spaces.models import Space
        from apps.campaigns.models import Campaign
        if obj.role == 'advertiser':
            return Campaign.objects.filter(advertiser=obj).count()
        return Space.objects.filter(owner=obj).count()
