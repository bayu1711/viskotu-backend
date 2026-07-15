from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CreativeAssetViewSet

router = DefaultRouter()
router.register(r'', CampaignViewSet, basename='campaign')

assets_router = DefaultRouter()
assets_router.register(r'', CreativeAssetViewSet, basename='creative-asset')

urlpatterns = [
    path('', include(router.urls)),
]
