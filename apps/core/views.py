from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from .models import SiteSettings, SupportTicket, SLAEvent, Category, ItemType, SurfaceMaterial, PointOfInterest
from .serializers import (
    SiteSettingsSerializer, SupportTicketSerializer, SLAEventSerializer,
    CategorySerializer, ItemTypeSerializer, SurfaceMaterialSerializer, PointOfInterestSerializer
)


class TaxonomyView(APIView):
    permission_classes = [permissions.AllowAny]

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


class SiteSettingsView(APIView):
    """
    GET /api/v1/core/settings/ — Publicly accessible endpoint to fetch Privacy Policy & Terms.
    PATCH/PUT /api/v1/core/settings/ — Admin-only endpoint to update policies.
    """
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        settings_obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def patch(self, request):
        if not self._is_admin(request.user):
            return Response(
                {'detail': 'Admin permissions required to update platform settings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        settings_obj = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        return self.patch(request)

    def _is_admin(self, user):
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            return True
        if getattr(user, 'role', None) == 'admin':
            return True
        return False


class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin':
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=user)


class SLAEventViewSet(viewsets.ModelViewSet):
    queryset = SLAEvent.objects.all()
    serializer_class = SLAEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin':
            return SLAEvent.objects.all()
        return SLAEvent.objects.none()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ItemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ItemType.objects.filter(is_active=True)
    serializer_class = ItemTypeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class SurfaceMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SurfaceMaterial.objects.filter(is_active=True)
    serializer_class = SurfaceMaterialSerializer
    permission_classes = [permissions.AllowAny]

class PointOfInterestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PointOfInterest.objects.all()
    serializer_class = PointOfInterestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs
