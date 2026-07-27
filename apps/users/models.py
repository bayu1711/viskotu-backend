from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('advertiser', 'Advertiser'),
        ('space-owner', 'Space Owner'),
        ('production-partner', 'Production Partner'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='advertiser')
    country = models.CharField(max_length=2, blank=True)
    preferred_currency = models.CharField(max_length=3, default='USD')
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # OTP verification
    otp_code = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    # Profile extras
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    # Business Profile
    account_type = models.CharField(max_length=20, default='personal')
    business_type = models.CharField(max_length=50, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    # KYC / verification
    kyc_status = models.CharField(
        max_length=20,
        choices=[('unverified', 'Unverified'), ('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')],
        default='unverified'
    )
    onboarded_roles = models.JSONField(default=list, blank=True)
    reliability_score = models.IntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} ({self.role})'

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def send_verification_email(self, request=None):
        import random
        from django.utils import timezone
        
        # Generate 6 digit OTP
        otp = f"{random.randint(100000, 999999)}"
        self.otp_code = otp
        self.otp_created_at = timezone.now()
        self.save(update_fields=['otp_code', 'otp_created_at'])

        sent_count = send_mail(
            subject='Verify your Viskotu email address',
            message=f'Your verification code is: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            html_message=f'<p>Hi {self.name},</p><p>Your email verification code is: <strong>{otp}</strong></p><p>This code expires in 15 minutes.</p><p>Thank you,<br/>Viskotu Team</p>',
            fail_silently=True,
        )
        return sent_count > 0

class AdvertiserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advertiser_profile')
    industry = models.CharField(max_length=100, blank=True)
    monthly_budget = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.user.name}'s Advertiser Profile"

class SpaceOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='space_owner_profile')
    number_of_spaces = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.user.name}'s Space Owner Profile"

class ProductionPartnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='production_partner_profile')
    location = models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    lead_time = models.CharField(max_length=50, blank=True)
    price_tier = models.CharField(max_length=10, default='$$')
    specialties = models.JSONField(default=list, blank=True)
    is_host_selectable = models.BooleanField(default=True)
    is_platform_network = models.BooleanField(default=True)
    production_lead_days = models.IntegerField(default=5)
    shipping_days = models.IntegerField(default=3)
    capacity = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.name}'s Production Profile"

class ManagedAccess(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_access')
    managed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_by', null=True, blank=True)
    invited_email = models.EmailField(blank=True)
    permissions = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('active', 'Active')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'managed_access'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner.email} -> {self.managed_user.email if self.managed_user else self.invited_email}"

