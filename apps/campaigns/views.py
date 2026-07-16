from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Campaign, CreativeAsset
from .serializers import (
    CampaignSerializer, CampaignListSerializer, CreativeAssetSerializer,
)


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
        qs = CreativeAsset.objects.filter(advertiser=self.request.user)
        campaign_id = self.request.query_params.get('campaign')
        if campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    def create(self, request, *args, **kwargs):
        """Handle multipart file upload."""
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={
            'name': request.data.get('name', file.name),
            'asset_type': request.data.get('asset_type', 'image'),
            'campaign': request.data.get('campaign'),
            'file': file,
            'file_size': file.size,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
