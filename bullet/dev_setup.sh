#!/bin/bash

# Wait for postgres
while :
do
    (echo -n > /dev/tcp/db/5432) >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        break
    fi
    sleep 1
done

python manage.py migrate
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username=admin --email=admin@localhost --no-input
python manage.py loaddata branchcountry
