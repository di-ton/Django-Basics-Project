#!/bin/bash

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 sciProSpace.wsgi