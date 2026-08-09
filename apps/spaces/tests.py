from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.spaces.models import Space, SpaceAvailability
from apps.core.models import Category
import datetime

User = get_user_model()


class SpaceAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='space_owner@example.com',
            password='Password123!',
            role='space-owner'
        )
        self.other_user = User.objects.create_user(
            email='other_user@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.category = Category.objects.create(name='fixed', description='Fixed Spaces')
        self.space = Space.objects.create(
            owner=self.owner,
            name='Times Square Billboard',
            category=self.category,
            base_rate='500.00',
            billing_period='daily',
            status='available',
            city='New York',
            state='NY'
        )

    def test_list_spaces_public_filtering(self):
        # Public browse only shows available spaces by default
        paused_space = Space.objects.create(
            owner=self.owner,
            name='Paused Wall Banner',
            category=self.category,
            base_rate='100.00',
            status='paused'
        )
        url = reverse('space-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain available space but not paused space
        space_ids = [s['id'] for s in response.data['results']]
        self.assertIn(str(self.space.id), space_ids)
        self.assertNotIn(str(paused_space.id), space_ids)

    def test_create_space_authenticated(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('space-list')
        data = {
            'name': 'Chicago Loop Display',
            'category': self.category.id,
            'base_rate': '350.00',
            'billing_period': 'daily',
            'city': 'Chicago',
            'state': 'IL'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Chicago Loop Display')
        created_space = Space.objects.get(id=response.data['id'])
        self.assertEqual(created_space.owner, self.owner)

    def test_mine_endpoint_shows_owner_listings(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('space-mine')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Times Square Billboard')

    def test_space_availability_endpoints(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse('space-availability', kwargs={'pk': self.space.id})
        data = {
            'date': '2026-11-01',
            'is_blocked': True,
            'reason': 'Scheduled Maintenance'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SpaceAvailability.objects.count(), 1)

        get_resp = self.client.get(url, format='json')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_resp.data), 1)
        self.assertEqual(get_resp.data[0]['reason'], 'Scheduled Maintenance')

    def test_pause_and_unpause_space(self):
        self.client.force_authenticate(user=self.owner)
        pause_url = reverse('space-pause', kwargs={'pk': self.space.id})
        response = self.client.post(pause_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.space.refresh_from_db()
        self.assertEqual(self.space.status, 'paused')

        unpause_url = reverse('space-unpause', kwargs={'pk': self.space.id})
        response = self.client.post(unpause_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.space.refresh_from_db()
        self.assertEqual(self.space.status, 'available')
