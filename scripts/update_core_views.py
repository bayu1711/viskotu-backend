import re

with open('apps/core/views.py', 'r') as f:
    content = f.read()

taxonomy_view = """
class TaxonomyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from .models import TaxonomyNode
        nodes = TaxonomyNode.objects.filter(is_active=True).order_by('category', 'sort_order')
        data = {}
        for node in nodes:
            if node.category not in data:
                data[node.category] = []
            data[node.category].append({
                'value': node.value,
                'label': node.label
            })
        return Response(data)
"""

if "TaxonomyView" not in content:
    content = content.replace("class SiteSettingsView", taxonomy_view + "\n\nclass SiteSettingsView")
    with open('apps/core/views.py', 'w') as f:
        f.write(content)

with open('apps/core/urls.py', 'r') as f:
    urls_content = f.read()

if "TaxonomyView" not in urls_content:
    urls_content = urls_content.replace(
        "from .views import SiteSettingsView, SupportTicketViewSet, SLAEventViewSet",
        "from .views import SiteSettingsView, SupportTicketViewSet, SLAEventViewSet, TaxonomyView"
    )
    urls_content = urls_content.replace(
        "path('settings/', SiteSettingsView.as_view(), name='site-settings'),",
        "path('settings/', SiteSettingsView.as_view(), name='site-settings'),\n    path('taxonomy/', TaxonomyView.as_view(), name='core-taxonomy'),"
    )
    with open('apps/core/urls.py', 'w') as f:
        f.write(urls_content)

