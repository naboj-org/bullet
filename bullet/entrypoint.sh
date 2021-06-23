#!/bin/sh

if [ "$DATABASE" = "bullet" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=bullet.settings.collect_static python3 manage.py collectstatic --no-input -i debug_toolbar

exec "$@"
