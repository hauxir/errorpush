#!/bin/bash
set -e

celery -A worker worker -l info &
CELERY_PID=$!

gunicorn --bind 0.0.0.0:5000 wsgi:app --access-logfile - &
GUNICORN_PID=$!

# If either process exits, kill the other and exit
wait -n $CELERY_PID $GUNICORN_PID
kill $CELERY_PID $GUNICORN_PID 2>/dev/null
exit 1
