#!/usr/bin/env bash
set -o errexit

python manage.py shell -c 'from django.conf import settings; databases = settings.DATABASES; default_database = databases.get("default") if isinstance(databases, dict) else None; engine = default_database.get("ENGINE") if isinstance(default_database, dict) else None; configured = engine == "django.db.backends.postgresql"; print("PostgreSQL database backend configured:", configured); assert configured, "Expected settings.DATABASES['default'] to use PostgreSQL before running migrations."'
python manage.py migrate
python manage.py collectstatic --noinput