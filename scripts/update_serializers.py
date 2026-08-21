import re

with open('apps/users/serializers.py', 'r') as f:
    content = f.read()

content = content.replace(
    "'city', 'state', 'address', 'account_type', 'business_type', 'company_size', 'tax_id',",
    "'city', 'state', 'address', 'account_type', 'business_type', 'company_size', 'tax_id', 'google_place_id',"
)

with open('apps/users/serializers.py', 'w') as f:
    f.write(content)

