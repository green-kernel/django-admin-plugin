#!/usr/bin/env bash
set -e

python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python - <<'PY'
import os
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(
    username=os.environ["DJANGO_SUPERUSER_USERNAME"],
    defaults={
        "email": os.environ.get("DJANGO_SUPERUSER_EMAIL",""),
        "is_staff": True, "is_superuser": True
    }
)
if created:
    u.set_password(os.environ["DJANGO_SUPERUSER_PASSWORD"])
    u.save()
    print("Superuser created")
else:
    print("Superuser already exists")
PY
fi

python manage.py runserver 0.0.0.0:8000
