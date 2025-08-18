#!/bin/sh

# Wait for Postgres to be available
if [ "$DB_ENGINE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_POSTGRESQL_HOST $DB_POSTGRESQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Make sure the application starts in a consistent state
if [[ -n "${UPDATE_STATICS}" ]]; then
  rm -rf /statictarget/*
  python manage.py collectstatic
  python manage.py migrate
fi
# Run the entrypoint command (for starting the app, it should be gunicorn ...)
# This is set by the docker-compose file for the running app.
exec "$@"
