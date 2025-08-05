#!/bin/sh

until 
    python manage.py migrate --check;
do
    echo "Waiting for the Migrations to be applied..."
    sleep 2
done

echo "Launching the service..."
exec "$@"
