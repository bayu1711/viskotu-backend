from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdPlacementViewSet

router = DefaultRouter()
router.register(r'', AdPlacementViewSet, basename='ad_placement')

urlpatterns = [
    path('', include(router.urls)),
]
