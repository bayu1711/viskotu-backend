from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.spaces.models import Space, SpaceAvailability
from apps.bookings.models import Booking
from apps.jobs.models import PrintJob
import datetime

User = get_user_model()


class BookingCreationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='Password123!',
            role='space-owner'
        )
        self.advertiser = User.objects.create_user(
            email='advertiser@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.space = Space.objects.create(
            owner=self.owner,
            name='Prime Highway Billboard',
            category='fixed',
            base_rate='100.00',
            billing_period='daily'
        )
        self.client.force_authenticate(user=self.advertiser)

    def test_create_booking_success(self):
        url = reverse('booking-list')
        data = {
            'space': str(self.space.id),
            'start_date': '2026-08-01',
            'end_date': '2026-08-10',
            'total_price': '1000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(str(response.data['advertiser']), str(self.advertiser.id))
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_booking_overlapping_failure(self):
        Booking.objects.create(
            advertiser=self.advertiser,
            space=self.space,
            start_date=datetime.date(2026, 8, 5),
            end_date=datetime.date(2026, 8, 15),
            total_price='1000.00',
            status='confirmed'
        )
        url = reverse('booking-list')
        data = {
            'space': str(self.space.id),
            'start_date': '2026-08-01',
            'end_date': '2026-08-10',
            'total_price': '1000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_booking_blocked_date_failure(self):
        SpaceAvailability.objects.create(
            space=self.space,
            date=datetime.date(2026, 8, 3),
            is_blocked=True,
            reason='Maintenance'
        )
        url = reverse('booking-list')
        data = {
            'space': str(self.space.id),
            'start_date': '2026-08-01',
            'end_date': '2026-08-10',
            'total_price': '1000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)


class BookingPrintJobTriggerTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner2@example.com',
            password='Password123!',
            role='space-owner'
        )
        self.advertiser = User.objects.create_user(
            email='advertiser2@example.com',
            password='Password123!',
            role='advertiser'
        )
        self.production_partner = User.objects.create_user(
            email='production_partner@example.com',
            password='Password123!',
            role='production-partner'
        )
        self.space = Space.objects.create(
            owner=self.owner,
            name='Downtown Wall Banner',
            category='fixed',
            base_rate='150.00',
            billing_period='daily'
        )
        self.booking = Booking.objects.create(
            advertiser=self.advertiser,
            space=self.space,
            start_date=datetime.date(2026, 9, 1),
            end_date=datetime.date(2026, 9, 15),
            total_price='2250.00',
            status='pending'
        )

    def test_status_change_to_confirmed_triggers_print_job(self):
        self.client.force_authenticate(user=self.advertiser)
        url = reverse('booking-detail', kwargs={'pk': self.booking.id})
        response = self.client.patch(url, {'status': 'confirmed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')
        self.assertTrue(hasattr(self.booking, 'print_job'))
        
        print_job = self.booking.print_job
        self.assertEqual(print_job.production_partner, self.production_partner)
        self.assertEqual(print_job.status, 'JOB_PENDING_ACCEPT')
        self.assertEqual(print_job.material, 'Standard Vinyl')
        self.assertEqual(print_job.size, '24x36')
