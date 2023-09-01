#!/bin/bash

python manage.py wait_for_database
python manage.py migrate
rm -rf uploads/
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --email=admin@naboj.org --no-input
python manage.py loaddata branchcountry
