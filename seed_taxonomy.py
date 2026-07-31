import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import TaxonomyNode

taxonomies = [
    # Company Size
    {'category': 'company_size', 'value': '1-10', 'label': '1-10 employees', 'sort_order': 1},
    {'category': 'company_size', 'value': '11-50', 'label': '11-50 employees', 'sort_order': 2},
    {'category': 'company_size', 'value': '51-200', 'label': '51-200 employees', 'sort_order': 3},
    {'category': 'company_size', 'value': '201+', 'label': '201+ employees', 'sort_order': 4},
    # Industry
    {'category': 'industry', 'value': 'technology', 'label': 'Technology', 'sort_order': 1},
    {'category': 'industry', 'value': 'retail', 'label': 'Retail', 'sort_order': 2},
    {'category': 'industry', 'value': 'food', 'label': 'Food & Beverage', 'sort_order': 3},
    {'category': 'industry', 'value': 'other', 'label': 'Other', 'sort_order': 4},
    # Monthly Budget
    {'category': 'monthly_budget', 'value': '0-1000', 'label': '$0 - $1,000', 'sort_order': 1},
    {'category': 'monthly_budget', 'value': '1000-5000', 'label': '$1,000 - $5,000', 'sort_order': 2},
    {'category': 'monthly_budget', 'value': '5000-10000', 'label': '$5,000 - $10,000', 'sort_order': 3},
    {'category': 'monthly_budget', 'value': '10000+', 'label': '$10,000+', 'sort_order': 4},
    # Primary Goal
    {'category': 'primary_goal', 'value': 'brand_awareness', 'label': 'Build Brand Awareness', 'sort_order': 1},
    {'category': 'primary_goal', 'value': 'foot_traffic', 'label': 'Drive Foot Traffic', 'sort_order': 2},
    {'category': 'primary_goal', 'value': 'lead_gen', 'label': 'Generate Leads or Sales', 'sort_order': 3},
    {'category': 'primary_goal', 'value': 'event_promo', 'label': 'Promote an Event', 'sort_order': 4},
    # Printer Capacity
    {'category': 'capacity', 'value': 'small', 'label': 'Small (1-10 jobs/week)', 'sort_order': 1},
    {'category': 'capacity', 'value': 'medium', 'label': 'Medium (11-25 jobs/week)', 'sort_order': 2},
    {'category': 'capacity', 'value': 'large', 'label': 'Large (26+ jobs/week)', 'sort_order': 3},
    # Number of spaces
    {'category': 'number_of_spaces', 'value': '1', 'label': '1 space', 'sort_order': 1},
    {'category': 'number_of_spaces', 'value': '2-5', 'label': '2-5 spaces', 'sort_order': 2},
    {'category': 'number_of_spaces', 'value': '6+', 'label': '6+ spaces', 'sort_order': 3},
]

for t in taxonomies:
    TaxonomyNode.objects.get_or_create(**t)

print("Seeded taxonomy")
