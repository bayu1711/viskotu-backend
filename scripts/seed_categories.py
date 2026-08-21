import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import Category

categories = [
    {'name': 'Vehicles', 'description': 'Cars, trucks, and other vehicles', 'icon': 'Car', 'sort_order': 1},
    {'name': 'Fixed Spaces', 'description': 'Buildings, apartments, and land', 'icon': 'Building', 'sort_order': 2},
    {'name': 'Gadgets', 'description': 'Phones, computers, and gadgets', 'icon': 'Smartphone', 'sort_order': 3},
    {'name': 'Lifestyle', 'description': 'Clothing, shoes, and accessories', 'icon': 'Shirt', 'sort_order': 4},
    {'name': 'Pets', 'description': 'Animals and pet supplies', 'icon': 'PawPrint', 'sort_order': 5},
    {'name': 'Sports & Outdoors', 'description': 'Sporting goods and equipment', 'icon': 'Trophy', 'sort_order': 6},
    {'name': 'Storefronts', 'description': 'Store fixtures and inventory', 'icon': 'Store', 'sort_order': 7},
    {'name': 'Accessories', 'description': 'Watches, jewelry, and more', 'icon': 'Watch', 'sort_order': 8},
]

for cat_data in categories:
    Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)

print("Seeded categories")
