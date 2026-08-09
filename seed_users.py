import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User

users = [
    {
        'email': 'admin@viskotu.com',
        'password': 'Admin1234!',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'is_email_verified': True,
        'kyc_status': 'verified',
    },
    {
        'email': 'spaceowner@viskotu.com',
        'password': 'Space1234!',
        'first_name': 'Sarah',
        'last_name': 'Owner',
        'role': 'space-owner',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True,
        'is_email_verified': True,
        'kyc_status': 'verified',
    },
    {
        'email': 'advertiser@viskotu.com',
        'password': 'Advert1234!',
        'first_name': 'Alex',
        'last_name': 'Advert',
        'role': 'advertiser',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True,
        'is_email_verified': True,
        'kyc_status': 'verified',
    },
    {
        'email': 'printer@viskotu.com',
        'password': 'Print1234!',
        'first_name': 'Pete',
        'last_name': 'Printer',
        'role': 'printer',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True,
        'is_email_verified': True,
        'kyc_status': 'verified',
    },
]

for u in users:
    password = u.pop('password')
    user, created = User.objects.get_or_create(email=u['email'], defaults=u)
    if created:
        user.set_password(password)
        user.save()
        print(f"  Created: {user.email} (role: {user.role})")
    else:
        print(f"  Already exists: {user.email}")

print("\nDone! Test credentials:")
print("  admin@viskotu.com        / Admin1234!   (admin + superuser)")
print("  spaceowner@viskotu.com   / Space1234!   (space-owner)")
print("  advertiser@viskotu.com   / Advert1234!  (advertiser)")
print("  printer@viskotu.com      / Print1234!   (production partner)")
