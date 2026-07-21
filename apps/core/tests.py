from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import SiteSettings

User = get_user_model()


class SiteSettingsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('site-settings')
        self.user = User.objects.create_user(
            email='normal@example.com',
            password='password123',
            role='advertiser'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )

    def test_get_settings_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('privacy_policy', response.data)
        self.assertIn('terms_of_service', response.data)

    def test_patch_settings_unauthenticated(self):
        response = self.client.patch(self.url, {'privacy_policy': 'New Policy'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_settings_normal_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'privacy_policy': 'New Policy'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_settings_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.url, {
            'privacy_policy': 'Updated Privacy Policy Content',
            'terms_of_service': 'Updated Terms of Service Content'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['privacy_policy'], 'Updated Privacy Policy Content')
        self.assertEqual(response.data['terms_of_service'], 'Updated Terms of Service Content')
