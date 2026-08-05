import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models import Category, ItemType, SurfaceMaterial

# Seed Surface Materials
materials = [
    'Vinyl Sticker',
    'Digital Screen',
    'Mesh Fabric',
    'Paper Poster',
    'Canvas',
    'Fabric',
    'Metal',
    'Glass'
]

for index, mat_name in enumerate(materials):
    mat, created = SurfaceMaterial.objects.get_or_create(
        name=mat_name,
        defaults={'description': f'{mat_name} material for ad placement', 'sort_order': index}
    )
    if created:
        print(f"Created SurfaceMaterial: {mat_name}")

# Seed Item Types per Category
item_types_data = {
    'Vehicles': ['Car Wrap', 'Truck Side', 'Van Wrap', 'Bus Wrap'],
    'Real Estate': ['Billboard', 'Window Graphic', 'Wall Banner', 'Building Wrap'],
    'Electronics': ['Digital Screen', 'TV Display', 'Tablet/Mobile'],
    'Apparel': ['T-Shirt', 'Backpack', 'Hat/Cap'],
    'Pets': ['Dog Vest', 'Pet Collar'],
    'Sports': ['Arena Board', 'Jersey/Uniform', 'Field Banner'],
    'Retail': ['Counter Display', 'A-Frame Sign', 'Poster Frame'],
    'Accessories': ['Keychain', 'Watch Strap']
}

for cat_name, types in item_types_data.items():
    try:
        cat = Category.objects.get(name=cat_name)
        for index, type_name in enumerate(types):
            it, created = ItemType.objects.get_or_create(
                name=type_name,
                category=cat,
                defaults={'description': f'{type_name} item type for {cat_name}', 'sort_order': index}
            )
            if created:
                print(f"Created ItemType: {type_name} under {cat_name}")
    except Category.DoesNotExist:
        print(f"Category {cat_name} not found, skipping item types.")

print("Seeding complete!")
