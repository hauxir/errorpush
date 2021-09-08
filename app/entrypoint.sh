#!/bin/bash
celery -A worker worker -l info &
gunicorn --bind 0.0.0.0:5000 wsgi:app --access-logfile -
