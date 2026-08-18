#!/bin/sh
set -eu

python manage.py migrate --noinput
# O Gunicorn sempre usa este endpoint interno e neutro do container. WEB_PORT
# regula apenas a publicação no host pelo Compose e o proxy, nunca este bind.
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
