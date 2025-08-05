#!/bin/sh

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Сollecting Static..."
python manage.py collectstatic --noinput

echo "Loading Fixtures..."
python manage.py loaddata dumps/awardtypes_data.json
python manage.py loaddata dumps/blogsections_data.json
python manage.py loaddata dumps/celery_beat_data.json

echo "Starting the app..."
exec "$@"
