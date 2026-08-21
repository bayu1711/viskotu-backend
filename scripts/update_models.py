import re

with open('apps/users/models.py', 'r') as f:
    content = f.read()

content = content.replace(
    '    company_name = models.CharField(max_length=200, blank=True)',
    '    company_name = models.CharField(max_length=200, blank=True)\n    google_place_id = models.CharField(max_length=255, blank=True)'
)

with open('apps/users/models.py', 'w') as f:
    f.write(content)

