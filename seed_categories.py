import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import Category

categories = [
    {'name': 'vehicles', 'description': 'Cars, trucks, and other vehicles', 'icon': 'Car', 'sort_order': 1},
    {'name': 'fixed', 'description': 'Buildings, apartments, and land', 'icon': 'Building', 'sort_order': 2},
    {'name': 'gadgets', 'description': 'Phones, computers, and gadgets', 'icon': 'Smartphone', 'sort_order': 3},
    {'name': 'lifestyle', 'description': 'Clothing, shoes, and accessories', 'icon': 'Shirt', 'sort_order': 4},
    {'name': 'pets', 'description': 'Animals and pet supplies', 'icon': 'PawPrint', 'sort_order': 5},
    {'name': 'sports', 'description': 'Sporting goods and equipment', 'icon': 'Trophy', 'sort_order': 6},
    {'name': 'storefronts', 'description': 'Store fixtures and inventory', 'icon': 'Store', 'sort_order': 7},
    {'name': 'accessories', 'description': 'Watches, jewelry, and more', 'icon': 'Watch', 'sort_order': 8},
]

for cat_data in categories:
    Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)

print("Seeded categories")
