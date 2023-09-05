#!/bin/bash

env="${1:-prod}"

python manage.py wait_for_database

if [ "$env" = "worker" ]; then
  exec python manage.py rqworker default
fi

python manage.py migrate

if [ "$env" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  python manage.py collectstatic --no-input
  exec uwsgi uwsgi.ini --wsgi-file=bullet/wsgi.py
fi
