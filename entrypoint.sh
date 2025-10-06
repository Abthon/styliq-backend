#!/usr/bin/env bash
set -e

# For Render deployment, use the Render PostgreSQL host
DB_HOST=${DB_HOST:-"dpg-d3huvuali9vc739979hg-a"}
DB_PORT=${DB_PORT:-"5432"}

# Wait for Postgres to be ready
echo "⏳ Waiting for Postgres at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Postgres is up—continuing."

# Now run migrations, collectstatic, and launch server
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn StyliQ.wsgi:application --bind 0.0.0.0:${PORT:-8000}
