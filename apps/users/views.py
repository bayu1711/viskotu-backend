from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from apps.core.services.email_service import send_welcome_email
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import action
import boto3
import logging

logger = logging.getLogger(__name__)

from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer,
    ChangeRoleSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, VerifyEmailSerializer,
    AdvertiserProfileSerializer, SpaceOwnerProfileSerializer,
    ProductionPartnerProfileSerializer,
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_sent = user.send_verification_email(request)
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'email_sent': email_sent,
            **tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            **tokens,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # Already blacklisted or invalid — treat as success
        return Response({'detail': 'Logged out.'}, status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        
        # Handle Advertiser Profile
        advertiser_data = request.data.pop('advertiser_profile', None)
        if advertiser_data is not None:
            from .models import AdvertiserProfile
            profile, _ = AdvertiserProfile.objects.get_or_create(user=user)
            profile_serializer = AdvertiserProfileSerializer(profile, data=advertiser_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        # Handle Space Owner Profile
        space_owner_data = request.data.pop('space_owner_profile', None)
        if space_owner_data is not None:
            from .models import SpaceOwnerProfile
            profile, _ = SpaceOwnerProfile.objects.get_or_create(user=user)
            profile_serializer = SpaceOwnerProfileSerializer(profile, data=space_owner_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        # Handle Production Partner Profile
        production_data = request.data.pop('production_partner_profile', None)
        if production_data is not None:
            from .models import ProductionPartnerProfile
            profile, _ = ProductionPartnerProfile.objects.get_or_create(user=user)
            profile_serializer = ProductionPartnerProfileSerializer(profile, data=production_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SwitchRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.role = serializer.validated_data['role']
        request.user.save(update_fields=['role'])
        return Response(UserSerializer(request.user).data)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            send_welcome_email(user, reset_url=reset_url)
        return Response({'detail': 'If that email exists, a reset link has been sent.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, serializer.validated_data['token']):
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password reset successful.'})


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        otp = serializer.validated_data.get('otp')
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.otp_code or user.otp_code != otp:
            return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.utils import timezone
        from datetime import timedelta
        if not user.otp_created_at or timezone.now() > user.otp_created_at + timedelta(minutes=15):
            return Response({'detail': 'Verification code expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.otp_code = ''
        user.save(update_fields=['is_email_verified', 'otp_code'])
        return Response({'detail': 'Email verified.'})


class ResendVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email_sent = request.user.send_verification_email(request)
        if not email_sent:
            return Response({'detail': 'Failed to send verification email. Please check your email configuration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'detail': 'Verification email sent.'})

class UserViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.user.is_staff and self.action == 'list':
            from .serializers import AdminUserSerializer
            return AdminUserSerializer
        return UserSerializer
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], url_path='me/kyc-verify', permission_classes=[IsAuthenticated])
    def kyc_verify(self, request):
        user = request.user
        document = request.FILES.get('document') or request.FILES.get('frontImage')
        
        if not document:
            return Response({'error': 'No document provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_bytes = document.read()
        
        try:
            client = boto3.client('rekognition', region_name='us-east-1')
            response = client.detect_text(Image={'Bytes': image_bytes})
            extracted_text = " ".join([text['DetectedText'].lower() for text in response.get('TextDetections', [])])
        except Exception as e:
            logger.error(f"AWS Rekognition error: {e}")
            if not settings.DEBUG:
                return Response({'error': 'Failed to process identity document. Please try again or contact support.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # Fallback for local development only
            extracted_text = (user.first_name + " " + user.last_name).lower() if user.first_name else ""
        
        first_name = user.first_name.lower() if user.first_name else ''
        last_name = user.last_name.lower() if user.last_name else ''
        
        if (first_name and first_name in extracted_text) or (last_name and last_name in extracted_text):
            user.kyc_status = 'verified'
        else:
            user.kyc_status = 'rejected'
        user.save(update_fields=['kyc_status'])
        
        return Response({'status': user.kyc_status})

from .models import ManagedAccess
from .serializers import ManagedAccessSerializer

class ManagedAccessViewSet(viewsets.ModelViewSet):
    serializer_class = ManagedAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ManagedAccess.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        email = serializer.validated_data.get('invited_email')
        managed_user = User.objects.filter(email=email).first()
        status = 'active' if managed_user else 'pending'
        serializer.save(owner=self.request.user, managed_user=managed_user, status=status)

    @action(detail=False, methods=['get'])
    def accounts_i_manage(self, request):
        qs = ManagedAccess.objects.filter(managed_user=request.user, status='active')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        # Blacklist the current refresh token if provided
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response({'detail': 'Account deactivated successfully.'})


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'detail': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
import urllib.request
import json as stdlib_json

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        role = request.data.get('role', 'advertiser')
        
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = None

            # --- Try 1: Verify as a JWT ID token ---
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    google_requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
            except ValueError:
                pass  # Not an ID token — try as an OAuth2 access token below

            # --- Try 2: Verify as an OAuth2 access token via Google userinfo ---
            if idinfo is None:
                req = urllib.request.Request(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {token}'}
                )
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            idinfo = stdlib_json.loads(resp.read().decode())
                        else:
                            return Response(
                                {'error': 'Invalid Google token'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                except Exception:
                    return Response(
                        {'error': 'Invalid Google token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if not idinfo or 'email' not in idinfo:
                return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)

            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            # Check if user exists
            user = User.objects.filter(email=email).first()
            if not user:
                # Create user if they don't exist
                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    is_email_verified=True,  # Google emails are pre-verified
                    account_type='personal'  # Default to personal, can be updated later
                )
                user.set_unusable_password()
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db.models import Q
from .serializers import ProductionPartnerSerializer

class ProductionPartnerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductionPartnerSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role__in=['production-partner', 'production_partner']).select_related('production_partner_profile')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(production_partner_profile__location__icontains=search)
            )
            
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(production_partner_profile__location__icontains=location)
            
        return queryset


