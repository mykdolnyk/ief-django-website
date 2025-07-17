#!/bin/sh

echo "Running Migrations..."
python manage.py migrate --noinput

echo "Starting the app..."
exec "$@"