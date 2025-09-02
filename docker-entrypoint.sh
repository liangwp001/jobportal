#!/usr/bin/env bash
set -euo pipefail

# Default environment
: "${PORT:=12000}"
: "${DJANGO_SETTINGS_MODULE:=core.settings}"
: "${DJANGO_DEBUG:=False}"
: "${DATABASE_URL:=sqlite:////app/db.sqlite3}"

# Run migrations and collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Run server
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers ${GUNICORN_WORKERS:-3} \
  --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-60}
