#!/bin/bash


# Exit immediately if a command exist status != 0
set -e


# Waiting MySQL db container to start and accept connection
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 0.1
done


# Run my_shop migrations for MySQL DB
echo "Running migrations..."
python manage.py migrate --noinput


# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput


# Loading fixtures of My_Shop in MySQL DB
echo "Loading fixtures in DB..."
python manage.py loaddata ./fixtures/my_shop_data.json


# Starting NGINX, GUNICORN and Django app My_Shop
echo "Starting My_Shop..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.ini