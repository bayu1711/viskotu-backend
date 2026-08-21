import os
import glob

apps_dir = 'apps'
for app_dir in os.listdir(apps_dir):
    full_path = os.path.join(apps_dir, app_dir)
    if os.path.isdir(full_path):
        admin_file = os.path.join(full_path, 'admin.py')
        if os.path.exists(admin_file):
            with open(admin_file, 'r') as f:
                content = f.read()
            
            if 'admin.site.register(model)' not in content:
                append_code = f"""
from django.apps import apps
try:
    app = apps.get_app_config('{app_dir}')
    for model_name, model in app.models.items():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
"""
                with open(admin_file, 'a') as f:
                    f.write(append_code)
