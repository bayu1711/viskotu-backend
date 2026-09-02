from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Campaign, CreativeAsset, CampaignObjective, TargetingRegion, TargetingMethod
from .serializers import (
    CampaignSerializer, CampaignListSerializer, CreativeAssetSerializer,
    CampaignObjectiveSerializer, TargetingRegionSerializer, TargetingMethodSerializer,
)


class CampaignObjectiveViewSet(viewsets.ModelViewSet):
    """
    - GET /campaigns/objectives/  → list all active objectives (anyone authenticated)
    - POST/PUT/PATCH/DELETE       → admin only
    """
    serializer_class = CampaignObjectiveSerializer

    def get_queryset(self):
        return CampaignObjective.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TargetingRegionViewSet(viewsets.ModelViewSet):
    """
    - GET /campaigns/regions/  → list all active regions
    - POST/PUT/PATCH/DELETE    → admin only
    """
    serializer_class = TargetingRegionSerializer

    def get_queryset(self):
        return TargetingRegion.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class TargetingMethodViewSet(viewsets.ModelViewSet):
    """
    - GET /campaigns/methods/  → list all active targeting methods
    - POST/PUT/PATCH/DELETE    → admin only
    """
    serializer_class = TargetingMethodSerializer

    def get_queryset(self):
        return TargetingMethod.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class CampaignViewSet(viewsets.ModelViewSet):
    """
    - GET /campaigns/            → my campaigns list
    - GET /campaigns/{id}/       → campaign detail
    - POST /campaigns/           → create campaign
    - PATCH /campaigns/{id}/     → update campaign
    - DELETE /campaigns/{id}/    → delete campaign
    - POST /campaigns/{id}/pause/   → pause
    - POST /campaigns/{id}/resume/  → resume
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'objective', 'status']
    ordering_fields = ['created_at', 'budget', 'spend', 'impressions']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return Campaign.objects.all().prefetch_related('assets')
        return Campaign.objects.filter(advertiser=user).prefetch_related('assets')

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status not in ('active', 'live_pending_pop'):
            return Response(
                {'detail': f'Cannot pause a campaign with status "{campaign.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign.status = 'paused'
        campaign.save(update_fields=['status'])
        return Response(CampaignSerializer(campaign, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != 'paused':
            return Response(
                {'detail': f'Cannot resume a campaign with status "{campaign.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign.status = 'active'
        campaign.save(update_fields=['status'])
        return Response(CampaignSerializer(campaign, context={'request': request}).data)


class CreativeAssetViewSet(viewsets.ModelViewSet):
    """
    - GET /creative-assets/        → my assets
    - POST /creative-assets/       → upload new asset
    - PATCH /creative-assets/{id}/ → update asset
    - DELETE /creative-assets/{id}/ → delete
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreativeAssetSerializer
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.role == 'admin':
            qs = CreativeAsset.objects.all()
        else:
            qs = CreativeAsset.objects.filter(advertiser=self.request.user)
            
        qs = qs.filter(is_archived=False)
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        return qs

    def get_serializer_class(self):
        if (self.request.user.is_staff or self.request.user.role == 'admin') and self.action in ['list', 'retrieve']:
            from .serializers import AdminCreativeAssetSerializer
            return AdminCreativeAssetSerializer
        return CreativeAssetSerializer

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    def create(self, request, *args, **kwargs):
        """Handle multipart file upload."""
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        import json
        dimensions = {}
        if 'dimensions' in request.data:
            try:
                dimensions = json.loads(request.data['dimensions'])
            except json.JSONDecodeError:
                pass

        serializer = self.get_serializer(data={
            'name': request.data.get('name', file.name),
            'asset_type': request.data.get('asset_type', 'image'),
            'campaign': request.data.get('campaign'),
            'file': file,
            'file_size': file.size,
            'dimensions': dimensions,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        asset = self.get_object()
        
        # Check associated campaigns
        # In our model, asset.campaign points to a single campaign, but the frontend
        # UI implies it could be used in multiple campaigns (it checks associatedCampaigns).
        # We'll check the direct `campaign` field, as well as if there are any other relations.
        # Based on models.py, a CreativeAsset belongs to ONE Campaign (ForeignKey).
        
        if asset.campaign:
            c_status = asset.campaign.status
            if c_status in ['active', 'live', 'in_progress', 'scheduled']:
                return Response({'detail': 'Cannot delete an asset used in an active campaign.'}, status=status.HTTP_400_BAD_REQUEST)
            elif c_status in ['completed', 'cancelled']:
                asset.is_archived = True
                asset.save()
                return Response({'detail': 'Asset archived.'}, status=status.HTTP_204_NO_CONTENT)
                
        # If no campaign or campaign is draft, hard delete
        return super().destroy(request, *args, **kwargs)
