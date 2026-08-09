from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ItemTypeViewSet, SurfaceMaterialViewSet, PointOfInterestViewSet,
    UsageTypeViewSet, PrintResolutionViewSet, AudienceBehaviorViewSet, TrafficDensityViewSet, PeakExposureViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'item-types', ItemTypeViewSet, basename='itemtype')
router.register(r'materials', SurfaceMaterialViewSet, basename='surfacematerial')
router.register(r'usage-types', UsageTypeViewSet, basename='usagetype')
router.register(r'print-resolutions', PrintResolutionViewSet, basename='printresolution')
router.register(r'audience-behaviors', AudienceBehaviorViewSet, basename='audiencebehavior')
router.register(r'traffic-densities', TrafficDensityViewSet, basename='trafficdensity')
router.register(r'peak-exposures', PeakExposureViewSet, basename='peakexposure')
router.register(r'pois', PointOfInterestViewSet, basename='poi')

urlpatterns = [
    path('', include(router.urls)),
]
