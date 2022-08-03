#!/bin/sh

python /code/manage.py makemigrations
python /code/manage.py migrate
python /code/manage.py collectstatic --noinput

exec "$@"
