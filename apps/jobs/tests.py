from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.spaces.models import Space
from apps.placements.models import AdPlacement
from apps.jobs.models import PrintJob
import datetime

User = get_user_model()


class PrintJobBiddingReroutingTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner_job@example.com',
            password='Password123!',
            role='space-owner'
        )
        self.advertiser = User.objects.create_user(
            email='advertiser_job@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.production_partner1 = User.objects.create_user(
            email='production_partner1@example.com',
            password='Password123!',
            role='production-partner'
        )
        self.production_partner2 = User.objects.create_user(
            email='production_partner2@example.com',
            password='Password123!',
            role='production-partner'
        )
        self.space = Space.objects.create(
            owner=self.owner,
            name='Highway Digital Screen',
            category='digital',
            base_rate='200.00',
            billing_period='daily'
        )
        self.ad_placement = AdPlacement.objects.create(
            advertiser=self.advertiser,
            space=self.space,
            start_date=datetime.date(2026, 10, 1),
            end_date=datetime.date(2026, 10, 10),
            total_price='2000.00',
            status='confirmed'
        )
        self.job = PrintJob.objects.create(
            ad_placement=self.ad_placement,
            production_partner=self.production_partner1,
            status='JOB_PENDING_ACCEPT',
            material='Standard Vinyl',
            size='24x36',
            quantity=1
        )

    def test_production_partner_accept_job(self):
        self.client.force_authenticate(user=self.production_partner1)
        url = reverse('job-accept', kwargs={'pk': self.job.id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'JOB_PREP')
        self.assertIsNotNone(self.job.accepted_at)

    def test_production_partner_reject_job_reroutes_to_second_printer(self):
        self.client.force_authenticate(user=self.production_partner1)
        url = reverse('job-reject', kwargs={'pk': self.job.id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.production_partner, self.production_partner2)
        self.assertEqual(self.job.status, 'JOB_PENDING_ACCEPT')
        self.assertIn(str(self.production_partner1.id), self.job.tried_production_partner_ids)
        self.assertEqual(self.job.reroute_count, 1)

    def test_production_partner_reject_when_no_printers_left_stalls_job(self):
        self.client.force_authenticate(user=self.production_partner1)
        url = reverse('job-reject', kwargs={'pk': self.job.id})
        self.client.post(url, format='json')

        self.client.force_authenticate(user=self.production_partner2)
        url = reverse('job-reject', kwargs={'pk': self.job.id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.job.refresh_from_db()
        self.assertIsNone(self.job.production_partner)
        self.assertEqual(self.job.status, 'JOB_STALLED')
        self.assertEqual(self.job.reroute_count, 2)
        self.assertIn(str(self.production_partner1.id), self.job.tried_production_partner_ids)
        self.assertIn(str(self.production_partner2.id), self.job.tried_production_partner_ids)

    def test_update_status_milestones(self):
        self.client.force_authenticate(user=self.production_partner1)
        url = reverse('job-update-status', kwargs={'pk': self.job.id})
        
        response = self.client.post(url, {'status': 'JOB_PRINTING'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'JOB_PRINTING')

        response = self.client.post(url, {'status': 'JOB_COMPLETED'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, 'JOB_COMPLETED')
        self.assertIsNotNone(self.job.completed_at)
