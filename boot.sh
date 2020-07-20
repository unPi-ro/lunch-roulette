#!/bin/bash

service ssh restart

source venv/bin/activate

# required for db upgrade
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

flask db upgrade
#flask translate compile

# let our flask app create logs
chown -R webot:webot .

exec gunicorn -b :80 -u webot -g webot --access-logfile - --error-logfile - roulette:app
