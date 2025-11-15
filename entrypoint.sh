#!/bin/bash

echo 'Running collectstatic......'
python manage.py collectstatic --no-input --settings=tournament_manager.settings

echo 'Applying migrations...'
python manage.py makemigrations --settings=tournament_manager.settings
python manage.py migrate --settings=tournament_manager.settings

echo 'Running Server...'
gunicorn --env DJANGO_SETTINGS_MODULE=tournament_manager.settings tournament_manager.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 180
