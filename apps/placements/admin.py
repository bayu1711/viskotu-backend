from django.contrib import admin

# Register your models here.

from django.apps import apps
try:
    app = apps.get_app_config('placements')
    for model_name, model in app.models.items():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
