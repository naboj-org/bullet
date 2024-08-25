#!/bin/bash

env="${1:-prod}"

if [ "$env" = "worker" ]; then
  exec python manage.py rqworker default
elif [ "$env" = "dev" ]; then
  python manage.py wait_for_database
fi

python manage.py migrate

if [ "$env" = "dev" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec multirun "gunicorn --bind 127.0.0.1:8001 --access-logfile - --log-file - bullet.wsgi" "caddy run --config /app/Caddyfile"
fi
