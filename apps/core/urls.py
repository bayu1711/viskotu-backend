from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteSettingsView, SupportTicketViewSet, SLAEventViewSet

router = DefaultRouter()
router.register(r'tickets', SupportTicketViewSet, basename='ticket')
router.register(r'sla-events', SLAEventViewSet, basename='sla-event')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/', SiteSettingsView.as_view(), name='site-settings'),
]
