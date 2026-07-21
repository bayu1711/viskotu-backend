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
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Profile extras
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    # KYC / verification
    kyc_status = models.CharField(
        max_length=20,
        choices=[('unverified', 'Unverified'), ('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')],
        default='unverified'
    )

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
        token = default_token_generator.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        verify_url = f"http://localhost:3000/verify-email?uid={uid}&token={token}"
        send_mail(
            subject="Verify your Viskotu email address",
            message=f"Hi {self.name},\n\nPlease click the link below to verify your email address:\n\n{verify_url}\n\nThank you,\nViskotu Team",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@viskotu.com'),
            recipient_list=[self.email],
            fail_silently=False,
        )
