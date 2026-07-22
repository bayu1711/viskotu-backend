from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ItemTypeViewSet, SurfaceMaterialViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'item-types', ItemTypeViewSet, basename='itemtype')
router.register(r'materials', SurfaceMaterialViewSet, basename='surfacematerial')

urlpatterns = [
    path('', include(router.urls)),
]
