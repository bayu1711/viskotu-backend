from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import ProductionPartnerProfile

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
            'role', 'is_email_verified', 'phone', 'avatar',
            'company_name', 'bio', 'kyc_status', 'created_at',
            'production_partner_profile', 'onboarded_roles',
        ]
        read_only_fields = ['id', 'email', 'is_email_verified', 'created_at']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
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
