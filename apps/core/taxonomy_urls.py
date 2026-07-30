from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ItemTypeViewSet, SurfaceMaterialViewSet, PointOfInterestViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'item-types', ItemTypeViewSet, basename='itemtype')
router.register(r'materials', SurfaceMaterialViewSet, basename='surfacematerial')
router.register(r'pois', PointOfInterestViewSet, basename='poi')

urlpatterns = [
    path('', include(router.urls)),
]
