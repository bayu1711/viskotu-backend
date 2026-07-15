"""Viskotu — root URL configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # OpenAPI schema & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/spaces/', include('apps.spaces.urls')),
    path('api/v1/campaigns/', include('apps.campaigns.urls')),
    path('api/v1/creative-assets/', include('apps.campaigns.asset_urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/jobs/', include('apps.jobs.urls')),
    path('api/v1/messages/', include('apps.messages.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
