from django.contrib import admin
from .models import Space, SpacePhoto, SpaceAvailability


class SpacePhotoInline(admin.TabularInline):
    model = SpacePhoto
    extra = 0
    readonly_fields = ['created_at']


class SpaceAvailabilityInline(admin.TabularInline):
    model = SpaceAvailability
    extra = 0


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'city', 'base_rate', 'billing_period', 'status', 'is_featured']
    list_filter = ['status', 'category', 'is_featured', 'fulfillment_type']
    search_fields = ['name', 'owner__email', 'city', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SpacePhotoInline, SpaceAvailabilityInline]

from django.apps import apps
try:
    app = apps.get_app_config('spaces')
    for model_name, model in app.models.items():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
