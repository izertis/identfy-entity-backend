#!/bin/sh

until python ./manage.py deploysetup
do
  echo "Retrying deploysetup command"
  sleep 5
done

python manage.py runserver 0.0.0.0:8000