import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime

from apps.users.models import User
from apps.spaces.models import Space, SpacePhoto
from apps.campaigns.models import Campaign, CreativeAsset
from apps.bookings.models import Booking
from apps.jobs.models import PrintJob


class Command(BaseCommand):
    help = 'Seed demo data for Viskotu platform (users, spaces, campaigns, jobs)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting demo data seeding...'))

        # 1. Create Demo Users
        users_data = [
            {
                'email': 'advertiser@demo.com',
                'first_name': 'Alex',
                'last_name': 'Advertiser',
                'role': 'advertiser',
                'company_name': 'Apex Brands Inc.',
                'phone': '+1 (555) 010-1001',
                'kyc_status': 'verified',
            },
            {
                'email': 'owner@demo.com',
                'first_name': 'Sarah',
                'last_name': 'Owner',
                'role': 'space-owner',
                'company_name': 'Urban Spaces LLC',
                'phone': '+1 (555) 010-2002',
                'kyc_status': 'verified',
            },
            {
                'email': 'production-partner@demo.com',
                'first_name': 'Paul',
                'last_name': 'Production Partner',
                'role': 'production_partner',
                'company_name': 'Prime Print & Install',
                'phone': '+1 (555) 010-3003',
                'kyc_status': 'verified',
            },
            {
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'company_name': 'Viskotu HQ',
                'phone': '+1 (555) 010-4004',
                'kyc_status': 'verified',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        users = {}
        for u_data in users_data:
            user, created = User.objects.get_or_create(
                email=u_data['email'],
                defaults={
                    'first_name': u_data.get('first_name', ''),
                    'last_name': u_data.get('last_name', ''),
                    'role': u_data['role'],
                    'company_name': u_data.get('company_name', ''),
                    'phone': u_data.get('phone', ''),
                    'kyc_status': u_data.get('kyc_status', 'verified'),
                    'is_email_verified': True,
                    'is_staff': u_data.get('is_staff', False),
                    'is_superuser': u_data.get('is_superuser', False),
                }
            )
            user.set_password('password123')
            user.save()
            users[u_data['role']] = user
            status_text = 'Created' if created else 'Updated'
            self.stdout.write(f"  [{status_text}] User: {user.email} ({user.role})")

        owner = users['space-owner']
        production_partner = users['production_partner']
        advertiser = users['advertiser']

        # 2. Create Demo Spaces
        spaces_data = [
            {
                'name': 'Downtown Main St. Glass Display',
                'description': 'High-traffic street-facing window display right next to the central metro station. Over 45,000 daily commuters pass by directly eye-level.',
                'category': 'fixed',
                'item_type': 'window',
                'address': '742 Market Street',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94103',
                'latitude': Decimal('37.785834'),
                'longitude': Decimal('-122.406417'),
                'width': Decimal('72.00'),
                'height': Decimal('48.00'),
                'material': 'Vinyl Sticker',
                'min_dpi': 300,
                'accepted_formats': ['pdf', 'png', 'ai'],
                'base_rate': Decimal('125.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': True,
                'impressions_estimate': '45,000/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
            {
                'name': 'Transit Delivery Fleet Van Wrap #104',
                'description': 'Full passenger side van wrap on active city delivery vehicle covering financial district and SoMa commercial corridors.',
                'category': 'vehicles',
                'item_type': 'van',
                'address': 'Mobile Corridor (SoMa/Financial)',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94105',
                'latitude': Decimal('37.789172'),
                'longitude': Decimal('-122.401447'),
                'width': Decimal('144.00'),
                'height': Decimal('60.00'),
                'material': 'Vinyl Sticker',
                'min_dpi': 150,
                'accepted_formats': ['pdf', 'ai'],
                'base_rate': Decimal('65.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': True,
                'impressions_estimate': '28,000/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
            {
                'name': 'Tech Hub Rooftop Billboard',
                'description': 'Massive illuminated exterior wall placement overlooking the freeway entrance right next to major tech campus offices.',
                'category': 'fixed',
                'item_type': 'billboard',
                'address': '101 Highway Overlook',
                'city': 'San Jose',
                'state': 'CA',
                'zip_code': '95110',
                'latitude': Decimal('37.338208'),
                'longitude': Decimal('-121.886329'),
                'width': Decimal('240.00'),
                'height': Decimal('120.00'),
                'material': 'Mesh',
                'min_dpi': 150,
                'accepted_formats': ['pdf', 'tiff'],
                'base_rate': Decimal('450.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': True,
                'impressions_estimate': '110,000/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
            {
                'name': 'Artisan Bakery Side Awning Display',
                'description': 'Charming fabric awning side banner located in high foot-traffic shopping lane near popular weekend farmers market.',
                'category': 'fixed',
                'item_type': 'wall',
                'address': '456 Valencia Street',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94110',
                'latitude': Decimal('37.764951'),
                'longitude': Decimal('-122.421898'),
                'width': Decimal('96.00'),
                'height': Decimal('36.00'),
                'material': 'Fabric Print',
                'min_dpi': 300,
                'accepted_formats': ['pdf', 'png'],
                'base_rate': Decimal('85.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': False,
                'impressions_estimate': '18,500/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
            {
                'name': 'Eco Courier E-Bike Rear Delivery Box',
                'description': 'Backside illuminated box panel on express food/package delivery e-bike navigating dense residential towers.',
                'category': 'vehicles',
                'item_type': 'bike',
                'address': 'Mission Bay Delivery Loop',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94158',
                'latitude': Decimal('37.771542'),
                'longitude': Decimal('-122.390888'),
                'width': Decimal('20.00'),
                'height': Decimal('20.00'),
                'material': 'Vinyl Sticker',
                'min_dpi': 300,
                'accepted_formats': ['png', 'jpg'],
                'base_rate': Decimal('25.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': False,
                'impressions_estimate': '9,200/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
            {
                'name': 'Austin Convention Center Corner Storefront',
                'description': 'Prime street-level window display right across from the West Entrance of the Austin Convention Center.',
                'category': 'fixed',
                'item_type': 'window',
                'address': '500 E 4th Street',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78701',
                'latitude': Decimal('30.264979'),
                'longitude': Decimal('-97.740350'),
                'width': Decimal('120.00'),
                'height': Decimal('72.00'),
                'material': 'Vinyl Sticker',
                'min_dpi': 300,
                'accepted_formats': ['pdf', 'ai'],
                'base_rate': Decimal('210.00'),
                'billing_period': 'daily',
                'status': 'available',
                'is_featured': True,
                'impressions_estimate': '62,000/day',
                'fulfillment_type': 'managed_printing',
                'preferred_production_partner': production_partner,
            },
        ]

        created_spaces = []
        for s_data in spaces_data:
            space, created = Space.objects.get_or_create(
                name=s_data['name'],
                owner=owner,
                defaults=s_data
            )
            created_spaces.append(space)
            self.stdout.write(f"  [Space] {space.name} (${space.base_rate}/{space.billing_period})")

        # 3. Create Demo Campaigns & Bookings
        if created_spaces:
            s1 = created_spaces[0]
            s2 = created_spaces[1]

            camp, _ = Campaign.objects.get_or_create(
                name='Q3 Summer Launch Surge',
                advertiser=advertiser,
                defaults={
                    'objective': 'brand_awareness',
                    'status': 'active',
                    'budget': Decimal('3500.00'),
                    'spend': Decimal('1850.00'),
                    'impressions': 342000,
                    'clicks': 4812,
                    'conversions': 310,
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + datetime.timedelta(days=30)).date(),
                    'target_locations': ['San Francisco, CA', 'Austin, TX'],
                }
            )
            self.stdout.write(f"  [Campaign] {camp.name} ({camp.status})")

            # Create Creative Asset
            asset, _ = CreativeAsset.objects.get_or_create(
                name='Summer_Surge_Main_Banner.pdf',
                advertiser=advertiser,
                campaign=camp,
                defaults={
                    'asset_type': 'pdf',
                    'file_size': 4820000,
                    'dimensions': {'width': 72, 'height': 48, 'dpi': 300},
                    'approval_status': 'approved',
                }
            )

            # Create Booking
            booking, _ = Booking.objects.get_or_create(
                advertiser=advertiser,
                space=s1,
                campaign=camp,
                defaults={
                    'status': 'confirmed',
                    'start_date': timezone.now().date(),
                    'end_date': (timezone.now() + datetime.timedelta(days=14)).date(),
                    'total_price': Decimal('1750.00'),
                    'platform_fee': Decimal('262.50'),
                    'paid_at': timezone.now(),
                }
            )
            self.stdout.write(f"  [Booking] {booking.id} ({booking.status})")

            # Create Print Job for Printer
            job, _ = PrintJob.objects.get_or_create(
                booking=booking,
                defaults={
                    'production_partner': production_partner,
                    'status': 'JOB_PRINTING',
                    'priority': 'high',
                    'material': s1.material,
                    'size': f"{s1.width}\" x {s1.height}\"",
                    'quantity': 1,
                    'deadline': timezone.now() + datetime.timedelta(days=3),
                    'accepted_at': timezone.now(),
                    'checklist': {
                        'artwork_verified': True,
                        'color_profile_matched': True,
                        'print_initiated': True,
                        'quality_check_passed': False,
                        'installation_ready': False,
                    }
                }
            )
            self.stdout.write(f"  [PrintJob] Job for {s1.name} assigned to {production_partner.company_name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo database!'))
