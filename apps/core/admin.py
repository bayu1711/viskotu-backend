from django.contrib import admin
from .models import SiteSettings


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
