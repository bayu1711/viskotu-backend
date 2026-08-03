from django.contrib import admin
from .models import SiteSettings, TaxonomyNode


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'updated_at']
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        # Limit to singleton instance
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of singleton settings
        return False


@admin.register(TaxonomyNode)
class TaxonomyNodeAdmin(admin.ModelAdmin):
    list_display = ['label', 'category', 'value', 'sort_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['label', 'value']
    ordering = ['category', 'sort_order', 'label']
    list_editable = ['sort_order', 'is_active']
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} item(s) marked as active.")
    make_active.short_description = "Mark selected items as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} item(s) marked as inactive.")
    make_inactive.short_description = "Mark selected items as inactive"


from django.apps import apps
try:
    app = apps.get_app_config('core')
    for model_name, model in app.models.items():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
