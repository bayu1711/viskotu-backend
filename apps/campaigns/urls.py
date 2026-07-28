from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, CreativeAssetViewSet,
    CampaignObjectiveViewSet, TargetingRegionViewSet, TargetingMethodViewSet,
)

router = DefaultRouter()
router.register(r'', CampaignViewSet, basename='campaign')
router.register(r'objectives', CampaignObjectiveViewSet, basename='campaign-objective')
router.register(r'regions', TargetingRegionViewSet, basename='targeting-region')
router.register(r'methods', TargetingMethodViewSet, basename='targeting-method')

assets_router = DefaultRouter()
assets_router.register(r'', CreativeAssetViewSet, basename='creative-asset')

urlpatterns = [
    path('', include(router.urls)),
]
