from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from apps.campaigns.models import Campaign, CreativeAsset

User = get_user_model()


class CampaignAPITests(APITestCase):
    def setUp(self):
        self.advertiser = User.objects.create_user(
            email='advertiser_campaign@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            name='Summer Promo Campaign',
            objective='brand_awareness',
            status='active',
            budget='5000.00'
        )
        self.client.force_authenticate(user=self.advertiser)

    def test_create_campaign(self):
        url = reverse('campaign-list')
        data = {
            'name': 'Fall Product Launch',
            'objective': 'product_launch',
            'budget': '10000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Fall Product Launch')
        created_campaign = Campaign.objects.get(id=response.data['id'])
        self.assertEqual(created_campaign.advertiser, self.advertiser)

    def test_pause_and_resume_campaign(self):
        pause_url = reverse('campaign-pause', kwargs={'pk': self.campaign.id})
        response = self.client.post(pause_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, 'paused')

        resume_url = reverse('campaign-resume', kwargs={'pk': self.campaign.id})
        response = self.client.post(resume_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, 'active')

    def test_upload_creative_asset(self):
        url = reverse('creative-asset-list')
        file_content = b'test file content mock image'
        file = SimpleUploadedFile('test_banner.jpg', file_content, content_type='image/jpeg')
        data = {
            'name': 'Main Banner Graphic',
            'asset_type': 'image',
            'campaign': str(self.campaign.id),
            'file': file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CreativeAsset.objects.count(), 1)
        asset = CreativeAsset.objects.first()
        self.assertEqual(asset.name, 'Main Banner Graphic')
        self.assertEqual(asset.advertiser, self.advertiser)
        self.assertEqual(asset.campaign, self.campaign)
