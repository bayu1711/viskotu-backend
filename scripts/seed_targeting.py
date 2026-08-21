import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.campaigns.models import TargetingRegion
from apps.core.models import PointOfInterest

REGIONS = [
    {'code': 'san-francisco', 'name': 'San Francisco', 'impressions': 2500000},
    {'code': 'los-angeles', 'name': 'Los Angeles', 'impressions': 4500000},
    {'code': 'chicago', 'name': 'Chicago', 'impressions': 3200000},
    {'code': 'singapore', 'name': 'Singapore', 'impressions': 5500000},
    {'code': 'new-york', 'name': 'New York', 'impressions': 8500000},
    {'code': 'london', 'name': 'London', 'impressions': 7500000},
    {'code': 'dubai', 'name': 'Dubai', 'impressions': 3100000},
    {'code': 'paris', 'name': 'Paris', 'impressions': 4200000},
    {'code': 'miami', 'name': 'Miami', 'impressions': 1800000},
]

for i, r in enumerate(REGIONS):
    TargetingRegion.objects.update_or_create(
        code=r['code'],
        defaults={'name': r['name'], 'impressions': r['impressions'], 'order': i}
    )

POIS = [
    {'name': 'Times Square', 'category': 'Entertainment', 'lat': 40.7580, 'lng': -73.9855},
    {'name': 'Central Park', 'category': 'Park', 'lat': 40.7812, 'lng': -73.9665},
    {'name': 'Marina Bay Sands', 'category': 'Landmark', 'lat': 1.2834, 'lng': 103.8607},
    {'name': 'Burj Khalifa', 'category': 'Landmark', 'lat': 25.1972, 'lng': 55.2744},
    {'name': 'Eiffel Tower', 'category': 'Landmark', 'lat': 48.8584, 'lng': 2.2945},
]

for p in POIS:
    PointOfInterest.objects.update_or_create(
        name=p['name'],
        defaults={'category': p['category'], 'lat': p['lat'], 'lng': p['lng']}
    )

print("Targeting Regions and POIs seeded successfully.")
