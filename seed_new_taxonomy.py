import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import (
    Orientation, PhysicalShape, QualityStandard,
    AudienceBehavior, TrafficDensity, PeakExposure, BillingPeriod, ProofOfPlayMethod,
    UsageType, PrintResolution
)

taxonomies = {
    Orientation: [
        {'value': 'portrait', 'label': 'Portrait', 'sort_order': 1},
        {'value': 'landscape', 'label': 'Landscape', 'sort_order': 2},
        {'value': 'square', 'label': 'Square', 'sort_order': 3},
    ],
    PhysicalShape: [
        {'value': 'rectangle', 'label': 'Rectangle', 'sort_order': 1},
        {'value': 'circle', 'label': 'Circle/Oval', 'sort_order': 2},
        {'value': 'custom', 'label': 'Custom Contour', 'sort_order': 3},
    ],
    QualityStandard: [
        {'value': 'res_72', 'label': '72 DPI', 'sort_order': 1},
        {'value': 'res_150', 'label': '150 DPI', 'sort_order': 2},
        {'value': 'res_300', 'label': '300 DPI', 'sort_order': 3},
    ],
    AudienceBehavior: [
        {'value': 'commuters', 'label': 'Commuters', 'sort_order': 1},
        {'value': 'shoppers', 'label': 'Shoppers', 'sort_order': 2},
        {'value': 'tourists', 'label': 'Tourists', 'sort_order': 3},
        {'value': 'students', 'label': 'Students', 'sort_order': 4},
        {'value': 'local_residents', 'label': 'Local Residents', 'sort_order': 5},
    ],
    TrafficDensity: [
        {'value': 'low', 'label': 'Low', 'sort_order': 1},
        {'value': 'medium', 'label': 'Medium', 'sort_order': 2},
        {'value': 'high', 'label': 'High', 'sort_order': 3},
        {'value': 'very_high', 'label': 'Very High', 'sort_order': 4},
    ],
    PeakExposure: [
        {'value': 'morning', 'label': 'Morning Rush', 'sort_order': 1},
        {'value': 'lunch', 'label': 'Lunchtime', 'sort_order': 2},
        {'value': 'evening', 'label': 'Evening Rush', 'sort_order': 3},
        {'value': 'night', 'label': 'Night', 'sort_order': 4},
        {'value': 'weekends', 'label': 'Weekends', 'sort_order': 5},
    ],
    BillingPeriod: [
        {'value': 'hourly', 'label': 'per hour', 'sort_order': 1},
        {'value': 'daily', 'label': 'per day', 'sort_order': 2},
        {'value': 'weekly', 'label': 'per week', 'sort_order': 3},
        {'value': 'monthly', 'label': 'per month', 'sort_order': 4},
        {'value': 'yearly', 'label': 'per year', 'sort_order': 5},
        {'value': 'custom', 'label': 'custom period', 'sort_order': 6},
    ],
    ProofOfPlayMethod: [
        {'value': 'gps-photo', 'label': 'GPS-tagged Photo (App)', 'sort_order': 1},
        {'value': 'video-walkaround', 'label': 'Video Walk-around', 'sort_order': 2},
        {'value': 'digital-log', 'label': 'Digital Log (Screens only)', 'sort_order': 3},
    ],
    UsageType: [
        {'value': 'moving', 'label': 'Moving', 'sort_order': 1},
        {'value': 'roaming', 'label': 'Roaming', 'sort_order': 2},
        {'value': 'stationary', 'label': 'Stationary', 'sort_order': 3},
        {'value': 'event_based', 'label': 'Event-Based', 'sort_order': 4},
    ],
    PrintResolution: [
        {'value': 'res_72', 'label': '72 DPI', 'sort_order': 1},
        {'value': 'res_150', 'label': '150 DPI', 'sort_order': 2},
        {'value': 'res_300', 'label': '300 DPI', 'sort_order': 3},
    ]
}

for model_class, entries in taxonomies.items():
    model_class.objects.all().delete()
    for entry in entries:
        model_class.objects.get_or_create(value=entry['value'], defaults=entry)
        print(f"Seeded {model_class.__name__}: {entry['label']}")

print("New taxonomies seeded successfully!")
