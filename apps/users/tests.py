from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class UserSignupTests(APITestCase):
    def test_signup_success(self):
        url = reverse('auth-signup')
        data = {
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'advertiser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')

        # Check email was sent via Django's send_mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'testuser@example.com')

    def test_signup_password_mismatch(self):
        url = reverse('auth-signup')
        data = {
            'email': 'badpass@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'DifferentPassword123!',
            'role': 'advertiser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='loginuser@example.com',
            password='Password123!',
            role='advertiser'
        )

    def test_login_success(self):
        url = reverse('auth-login')
        data = {'email': 'loginuser@example.com', 'password': 'Password123!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_failure(self):
        url = reverse('auth-login')
        data = {'email': 'loginuser@example.com', 'password': 'WrongPassword!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='unverified@example.com',
            password='Password123!',
            role='advertiser'
        )

    def test_verify_email_success(self):
        self.assertFalse(self.user.is_email_verified)
        self.user.otp_code = '123456'
        from django.utils import timezone
        self.user.otp_created_at = timezone.now()
        self.user.save()

        url = reverse('auth-verify-email')
        data = {'email': self.user.email, 'otp': '123456'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_invalid_token(self):
        self.user.otp_code = '123456'
        from django.utils import timezone
        self.user.otp_created_at = timezone.now()
        self.user.save()

        url = reverse('auth-verify-email')
        data = {'email': self.user.email, 'otp': '000000'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)

    def test_resend_verification_email(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-resend-verification')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'unverified@example.com')


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='resetuser@example.com',
            password='OldPassword123!',
            role='advertiser'
        )

    def test_password_reset_flow(self):
        # 1. Request password reset
        request_url = reverse('auth-password-reset')
        response = self.client.post(request_url, {'email': 'resetuser@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset Your Viskotu Password', mail.outbox[0].subject)

        # 2. Confirm password reset using valid uid and token
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        confirm_url = reverse('auth-password-reset-confirm')
        response = self.client.post(confirm_url, {
            'uid': uid,
            'token': token,
            'new_password': 'NewPassword123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verify user can log in with new password
        login_url = reverse('auth-login')
        response = self.client.post(login_url, {
            'email': 'resetuser@example.com',
            'password': 'NewPassword123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RoleSwitchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='roleuser@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.client.force_authenticate(user=self.user)

    def test_switch_role_success(self):
        url = reverse('auth-switch-role')
        response = self.client.post(url, {'role': 'space-owner'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'space-owner')


class ProductionPartnerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.partner_user = User.objects.create_user(
            email='partner@example.com',
            password='Password123!',
            role='production-partner',
            first_name='Print',
            last_name='Shop'
        )
        from .models import ProductionPartnerProfile
        self.profile = ProductionPartnerProfile.objects.create(
            user=self.partner_user,
            location='Dallas, TX',
            rating=4.8,
            price_tier='$$$',
            specialties=['Vinyl', 'Banner']
        )
        self.client.force_authenticate(user=self.user)

    def test_list_partners_success(self):
        url = '/api/v1/production-partners/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        partner_data = response.data['results'][0]
        self.assertEqual(partner_data['name'], 'Print Shop')
        self.assertEqual(partner_data['location'], 'Dallas, TX')
        self.assertEqual(partner_data['priceTier'], '$$$')
        self.assertEqual(partner_data['rating'], 4.8)
        self.assertEqual(partner_data['specialties'], ['Vinyl', 'Banner'])

    def test_search_partners(self):
        url = '/api/v1/production-partners/?search=Dallas'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        url = '/api/v1/production-partners/?search=New York'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

