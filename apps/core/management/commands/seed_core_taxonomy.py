import uuid
from django.core.management.base import BaseCommand
from apps.core.models import TaxonomyNode

class Command(BaseCommand):
    help = 'Seed core taxonomy data (industry, monthly_budget, primary_goal, company_size)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding core taxonomy...')

        taxonomy_data = {
            'industry': [
                {'value': 'technology', 'label': 'Technology'},
                {'value': 'retail', 'label': 'Retail'},
                {'value': 'food', 'label': 'Food & Beverage'},
                {'value': 'healthcare', 'label': 'Healthcare'},
                {'value': 'education', 'label': 'Education'},
                {'value': 'real_estate', 'label': 'Real Estate'},
                {'value': 'finance', 'label': 'Finance'},
                {'value': 'other', 'label': 'Other'},
            ],
            'monthly_budget': [
                {'value': '0-1000', 'label': '$0 - $1,000'},
                {'value': '1000-5000', 'label': '$1,000 - $5,000'},
                {'value': '5000-10000', 'label': '$5,000 - $10,000'},
                {'value': '10000+', 'label': '$10,000+'},
            ],
            'primary_goal': [
                {'value': 'brand_awareness', 'label': 'Build Brand Awareness'},
                {'value': 'foot_traffic', 'label': 'Drive Foot Traffic'},
                {'value': 'lead_gen', 'label': 'Generate Leads or Sales'},
                {'value': 'event_promo', 'label': 'Promote an Event'},
            ],
            'company_size': [
                {'value': '1-10', 'label': '1-10 employees'},
                {'value': '11-50', 'label': '11-50 employees'},
                {'value': '51-200', 'label': '51-200 employees'},
                {'value': '201+', 'label': '201+ employees'},
            ]
        }

        for category, nodes in taxonomy_data.items():
            TaxonomyNode.objects.filter(category=category).delete()
            
            for index, node in enumerate(nodes):
                TaxonomyNode.objects.create(
                    category=category,
                    value=node['value'],
                    label=node['label'],
                    sort_order=index
                )
                self.stdout.write(f"  Added {category}: {node['label']}")

        self.stdout.write(self.style.SUCCESS('Core taxonomy seeding complete!'))
