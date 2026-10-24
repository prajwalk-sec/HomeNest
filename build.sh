#!/usr/bin/env bash
set -o errexit

python manage.py check
python manage.py shell -c 'import os; from django.conf import settings; databases = settings.DATABASES; default_database = databases.get("default") if isinstance(databases, dict) else None; engine = default_database.get("ENGINE") if isinstance(default_database, dict) else None; print("Django settings module:", settings.SETTINGS_MODULE); print("DATABASE_URL available:", bool(os.environ.get("DATABASE_URL", "").strip())); print("Database backend engine:", engine or "<missing>"); assert engine == "django.db.backends.postgresql", "Expected settings.DATABASES[default] to use django.db.backends.postgresql before running migrations."'
python manage.py migrate
python manage.py collectstatic --noinput