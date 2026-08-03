import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import CompanySize, Industry, MonthlyBudget, PrimaryGoal, PrinterCapacity, SpaceCount

taxonomies = {
    CompanySize: [
        {'value': '1-10', 'label': '1-10 employees', 'sort_order': 1},
        {'value': '11-50', 'label': '11-50 employees', 'sort_order': 2},
        {'value': '51-200', 'label': '51-200 employees', 'sort_order': 3},
        {'value': '201+', 'label': '201+ employees', 'sort_order': 4},
    ],
    Industry: [
        {'value': 'technology', 'label': 'Technology', 'sort_order': 1},
        {'value': 'retail', 'label': 'Retail', 'sort_order': 2},
        {'value': 'food', 'label': 'Food & Beverage', 'sort_order': 3},
        {'value': 'other', 'label': 'Other', 'sort_order': 4},
    ],
    MonthlyBudget: [
        {'value': '0-1000', 'label': '$0 - $1,000', 'sort_order': 1},
        {'value': '1000-5000', 'label': '$1,000 - $5,000', 'sort_order': 2},
        {'value': '5000-10000', 'label': '$5,000 - $10,000', 'sort_order': 3},
        {'value': '10000+', 'label': '$10,000+', 'sort_order': 4},
    ],
    PrimaryGoal: [
        {'value': 'brand_awareness', 'label': 'Build Brand Awareness', 'sort_order': 1},
        {'value': 'foot_traffic', 'label': 'Drive Foot Traffic', 'sort_order': 2},
        {'value': 'lead_gen', 'label': 'Generate Leads or Sales', 'sort_order': 3},
        {'value': 'event_promo', 'label': 'Promote an Event', 'sort_order': 4},
    ],
    PrinterCapacity: [
        {'value': 'small', 'label': 'Small (1-10 jobs/week)', 'sort_order': 1},
        {'value': 'medium', 'label': 'Medium (11-25 jobs/week)', 'sort_order': 2},
        {'value': 'large', 'label': 'Large (26+ jobs/week)', 'sort_order': 3},
    ],
    SpaceCount: [
        {'value': '1', 'label': '1 space', 'sort_order': 1},
        {'value': '2-5', 'label': '2-5 spaces', 'sort_order': 2},
        {'value': '6+', 'label': '6+ spaces', 'sort_order': 3},
    ]
}

for model_class, entries in taxonomies.items():
    for entry in entries:
        model_class.objects.get_or_create(value=entry['value'], defaults=entry)

print("Seeded taxonomy")
