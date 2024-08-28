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


# Collect static files (only needed for production)
echo "Collecting static files..."
python manage.py collectstatic --noinput


# Starting NGINX, GUNICORN and Django app My_Shop
echo "Starting My_Shop..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.ini