import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from apps.accounts.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@uav.com', 'admin123')
    print("Admin created: username=admin  password=admin123")
else:
    print("Admin already exists: username=admin  password=admin123")
