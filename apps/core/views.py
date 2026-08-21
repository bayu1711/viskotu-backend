from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from .models import SiteSettings, SupportTicket, SLAEvent, Category, ItemType, SurfaceMaterial, PointOfInterest, UsageType, PrintResolution, AudienceBehavior, TrafficDensity, PeakExposure, Report
from .serializers import (
    SiteSettingsSerializer, SupportTicketSerializer, SLAEventSerializer,
    CategorySerializer, ItemTypeSerializer, SurfaceMaterialSerializer, PointOfInterestSerializer,
    UsageTypeSerializer, PrintResolutionSerializer, AudienceBehaviorSerializer, TrafficDensitySerializer, PeakExposureSerializer, ReportSerializer
)


class TaxonomyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from .models import (
            CompanySize, Industry, MonthlyBudget, PrimaryGoal, PrinterCapacity, SpaceCount,
            Orientation, PhysicalShape, QualityStandard, AudienceBehavior, TrafficDensity, PeakExposure, BillingPeriod, ProofOfPlayMethod
        )
        
        data = {
            'company_size': [{'value': obj.value, 'label': obj.label} for obj in CompanySize.objects.filter(is_active=True)],
            'industry': [{'value': obj.value, 'label': obj.label} for obj in Industry.objects.filter(is_active=True)],
            'monthly_budget': [{'value': obj.value, 'label': obj.label} for obj in MonthlyBudget.objects.filter(is_active=True)],
            'primary_goal': [{'value': obj.value, 'label': obj.label} for obj in PrimaryGoal.objects.filter(is_active=True)],
            'capacity': [{'value': obj.value, 'label': obj.label} for obj in PrinterCapacity.objects.filter(is_active=True)],
            'number_of_spaces': [{'value': obj.value, 'label': obj.label} for obj in SpaceCount.objects.filter(is_active=True)],
            'orientation': [{'value': obj.value, 'label': obj.label} for obj in Orientation.objects.filter(is_active=True)],
            'physical_shape': [{'value': obj.value, 'label': obj.label} for obj in PhysicalShape.objects.filter(is_active=True)],
            'quality_standard': [{'value': obj.value, 'label': obj.label} for obj in QualityStandard.objects.filter(is_active=True)],
            'print_resolution': [{'value': obj.value, 'label': f"{obj.label} - {obj.description}" if obj.description else obj.label} for obj in PrintResolution.objects.filter(is_active=True)],
            'usage_type': [{'value': obj.value, 'label': obj.label} for obj in UsageType.objects.filter(is_active=True)],
            'audience_behavior': [{'value': obj.value, 'label': obj.label} for obj in AudienceBehavior.objects.filter(is_active=True)],
            'traffic_density': [{'value': obj.value, 'label': obj.label} for obj in TrafficDensity.objects.filter(is_active=True)],
            'peak_exposure': [{'value': obj.value, 'label': obj.label} for obj in PeakExposure.objects.filter(is_active=True)],
            'billing_period': [{'value': obj.value, 'label': obj.label} for obj in BillingPeriod.objects.filter(is_active=True)],
            'proof_of_play_method': [{'value': obj.value, 'label': obj.label} for obj in ProofOfPlayMethod.objects.filter(is_active=True)],
        }
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

class UsageTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UsageType.objects.filter(is_active=True)
    serializer_class = UsageTypeSerializer
    permission_classes = [permissions.AllowAny]

class PrintResolutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PrintResolution.objects.filter(is_active=True)
    serializer_class = PrintResolutionSerializer
    permission_classes = [permissions.AllowAny]

class AudienceBehaviorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AudienceBehavior.objects.filter(is_active=True)
    serializer_class = AudienceBehaviorSerializer
    permission_classes = [permissions.AllowAny]

class TrafficDensityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrafficDensity.objects.filter(is_active=True)
    serializer_class = TrafficDensitySerializer
    permission_classes = [permissions.AllowAny]

class PeakExposureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PeakExposure.objects.filter(is_active=True)
    serializer_class = PeakExposureSerializer
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

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin':
            return Report.objects.all()
        return Report.objects.filter(reporter=user)
