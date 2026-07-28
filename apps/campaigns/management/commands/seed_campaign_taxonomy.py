"""
Management command to seed campaign taxonomy data:
  - CampaignObjective
  - TargetingRegion
  - TargetingMethod
Run with: python manage.py seed_campaign_taxonomy
"""
from django.core.management.base import BaseCommand
from apps.campaigns.models import CampaignObjective, TargetingRegion, TargetingMethod


OBJECTIVES = [
    {
        'code': 'route-targeting',
        'label': 'Route Targeting',
        'tag': 'A → B',
        'description': 'Target assets moving between specific locations (A to B). Perfect for commuter corridors and transit routes.',
        'order': 0,
    },
    {
        'code': 'zone-targeting',
        'label': 'Zone Targeting',
        'tag': 'City Zones',
        'description': 'Target assets operating within specific city boundaries or hubs — ideal for neighbourhood and district-level reach.',
        'order': 1,
    },
    {
        'code': 'fixed-spot-targeting',
        'label': 'Fixed Spot Targeting',
        'tag': 'Fixed Spots',
        'description': 'Target assets at specific high-traffic coordinates — billboards, screens, and static placements at precise locations.',
        'order': 2,
    },
    {
        'code': 'pulse-targeting',
        'label': 'Pulse Targeting',
        'tag': 'Time Windows',
        'description': 'Target high-density assets during specific time-windows or events. Surge your reach when it matters most.',
        'order': 3,
    },
]

REGIONS = [
    {'code': 'new-york', 'name': 'New York', 'impressions': 320000, 'order': 0},
    {'code': 'los-angeles', 'name': 'Los Angeles', 'impressions': 260000, 'order': 1},
    {'code': 'chicago', 'name': 'Chicago', 'impressions': 195000, 'order': 2},
    {'code': 'miami', 'name': 'Miami', 'impressions': 145000, 'order': 3},
    {'code': 'san-francisco', 'name': 'San Francisco', 'impressions': 172000, 'order': 4},
    {'code': 'seattle', 'name': 'Seattle', 'impressions': 118000, 'order': 5},
    {'code': 'austin', 'name': 'Austin', 'impressions': 98000, 'order': 6},
    {'code': 'toronto', 'name': 'Toronto', 'impressions': 152000, 'order': 7},
    {'code': 'london', 'name': 'London', 'impressions': 420000, 'order': 8},
    {'code': 'paris', 'name': 'Paris', 'impressions': 310000, 'order': 9},
    {'code': 'dubai', 'name': 'Dubai', 'impressions': 225000, 'order': 10},
    {'code': 'singapore', 'name': 'Singapore', 'impressions': 188000, 'order': 11},
    {'code': 'sydney', 'name': 'Sydney', 'impressions': 162000, 'order': 12},
    {'code': 'tokyo', 'name': 'Tokyo', 'impressions': 390000, 'order': 13},
    {'code': 'berlin', 'name': 'Berlin', 'impressions': 145000, 'order': 14},
    {'code': 'amsterdam', 'name': 'Amsterdam', 'impressions': 98000, 'order': 15},
    {'code': 'kuala-lumpur', 'name': 'Kuala Lumpur', 'impressions': 130000, 'order': 16},
    {'code': 'jakarta', 'name': 'Jakarta', 'impressions': 200000, 'order': 17},
]

METHODS = [
    {
        'code': 'route',
        'label': 'Target by Route',
        'description': 'Define a corridor between two points and target all ad spaces along that route.',
        'order': 0,
    },
    {
        'code': 'area',
        'label': 'Target by Region',
        'description': 'Select one or more geographic regions to target your campaign.',
        'order': 1,
    },
    {
        'code': 'spot',
        'label': 'Target by Spot',
        'description': 'Select a specific point of interest and set a radius for targeting.',
        'order': 2,
    },
]


class Command(BaseCommand):
    help = 'Seed campaign taxonomy data (objectives, regions, targeting methods)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding campaign objectives...')
        for obj in OBJECTIVES:
            instance, created = CampaignObjective.objects.update_or_create(
                code=obj['code'],
                defaults={k: v for k, v in obj.items() if k != 'code'},
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {instance.label}')

        self.stdout.write('Seeding targeting regions...')
        for reg in REGIONS:
            instance, created = TargetingRegion.objects.update_or_create(
                code=reg['code'],
                defaults={k: v for k, v in reg.items() if k != 'code'},
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {instance.name}')

        self.stdout.write('Seeding targeting methods...')
        for meth in METHODS:
            instance, created = TargetingMethod.objects.update_or_create(
                code=meth['code'],
                defaults={k: v for k, v in meth.items() if k != 'code'},
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {instance.label}')

        self.stdout.write(self.style.SUCCESS('Campaign taxonomy seeding complete!'))
