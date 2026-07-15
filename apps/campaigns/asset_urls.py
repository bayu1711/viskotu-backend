from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreativeAssetViewSet

router = DefaultRouter()
router.register(r'', CreativeAssetViewSet, basename='creative-asset')

urlpatterns = [
    path('', include(router.urls)),
]
