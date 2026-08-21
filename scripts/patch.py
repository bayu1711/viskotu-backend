import os

views_path = 'apps/users/views.py'
with open(views_path, 'r') as f:
    content = f.read()

content = content.replace("class UserViewSet(viewsets.ModelViewSet):", """class UserViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.user.is_staff and self.action == 'list':
            from .serializers import AdminUserSerializer
            return AdminUserSerializer
        return UserSerializer""")

with open(views_path, 'w') as f:
    f.write(content)

serializers_path = 'apps/users/serializers.py'
with open(serializers_path, 'r') as f:
    content = f.read()

if "AdminUserSerializer" not in content:
    content += """

class AdminUserSerializer(UserSerializer):
    revenue = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['revenue', 'assets']

    def get_revenue(self, obj):
        from apps.payments.models import Payment, Payout
        from django.db.models import Sum
        if obj.role == 'advertiser':
            return float(Payment.objects.filter(payer=obj, status='succeeded').aggregate(total=Sum('amount'))['total'] or 0)
        else:
            return float(Payout.objects.filter(recipient=obj, status='paid').aggregate(total=Sum('amount'))['total'] or 0)

    def get_assets(self, obj):
        from apps.spaces.models import Space
        from apps.campaigns.models import Campaign
        if obj.role == 'advertiser':
            return Campaign.objects.filter(advertiser=obj).count()
        return Space.objects.filter(owner=obj).count()
"""
    with open(serializers_path, 'w') as f:
        f.write(content)

