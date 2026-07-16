from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PrintJobViewSet

router = DefaultRouter()
router.register(r'', PrintJobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
