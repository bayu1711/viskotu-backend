import re

with open('apps/core/models.py', 'r') as f:
    content = f.read()

taxonomy_model = """
class TaxonomyNode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50) # e.g. 'industry', 'company_size', 'primary_goal', 'capacity'
    value = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'sort_order', 'label']

    def __str__(self):
        return f"{self.category}: {self.label}"
"""

if "class TaxonomyNode" not in content:
    content += "\n" + taxonomy_model
    with open('apps/core/models.py', 'w') as f:
        f.write(content)

