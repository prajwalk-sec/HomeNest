#!/usr/bin/env bash
set -o errexit

python manage.py shell -c 'from django.conf import settings; engine = settings.DATABASES["default"].get("ENGINE"); print("PostgreSQL database backend configured:", engine == "django.db.backends.postgresql"); assert engine == "django.db.backends.postgresql", "Expected the PostgreSQL database backend before running migrations."'
python manage.py migrate
python manage.py collectstatic --noinput