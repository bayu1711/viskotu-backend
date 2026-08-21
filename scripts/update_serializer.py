import re

with open('apps/users/serializers.py', 'r') as f:
    content = f.read()

if "'primary_goal'" not in content:
    content = content.replace(
        "fields = ['industry', 'monthly_budget']",
        "fields = ['industry', 'monthly_budget', 'primary_goal']"
    )
    
    with open('apps/users/serializers.py', 'w') as f:
        f.write(content)

