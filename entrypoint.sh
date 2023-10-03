#!/bin/sh

if [ "$DB_ENGINE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_POSTGRESQL_HOST $DB_POSTGRESQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
rm -rf /statictarget/*
python manage.py migrate
python manage.py collectstatic
exec "$@"

