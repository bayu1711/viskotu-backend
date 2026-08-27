from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import (
    CampaignViewSet, CreativeAssetViewSet,
    CampaignObjectiveViewSet, TargetingRegionViewSet, TargetingMethodViewSet,
)

# Taxonomy router — must be wired BEFORE the main campaign router so that
# /objectives/, /regions/, /methods/ are matched before {pk}/ captures them.
# Using SimpleRouter prevents it from generating a default API Root at `^$`
taxonomy_router = SimpleRouter()
taxonomy_router.register(r'objectives', CampaignObjectiveViewSet, basename='campaign-objective')
taxonomy_router.register(r'regions', TargetingRegionViewSet, basename='targeting-region')
taxonomy_router.register(r'methods', TargetingMethodViewSet, basename='targeting-method')

# Main campaign CRUD router — registered with empty prefix so it occupies /campaigns/
campaign_router = SimpleRouter()
campaign_router.register(r'', CampaignViewSet, basename='campaign')

assets_router = DefaultRouter()
assets_router.register(r'', CreativeAssetViewSet, basename='creative-asset')

urlpatterns = [
    # Taxonomy routes first so they are matched before the pk-catching campaign routes
    path('', include(taxonomy_router.urls)),
    path('', include(campaign_router.urls)),
]
