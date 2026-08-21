import re

with open('apps/users/models.py', 'r') as f:
    content = f.read()

if "primary_goal =" not in content:
    content = content.replace(
        "monthly_budget = models.CharField(max_length=50, blank=True)",
        "monthly_budget = models.CharField(max_length=50, blank=True)\n    primary_goal = models.CharField(max_length=50, blank=True)"
    )
    
    with open('apps/users/models.py', 'w') as f:
        f.write(content)

