import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.users.models import User
from apps.users.serializers import UserSerializer
user = User.objects.filter(email='advertiser@demo.com').first()
if user:
    print('is_email_verified from DB:', user.is_email_verified)
    print('is_email_verified from Serializer:', UserSerializer(user).data.get('is_email_verified'))
