#!/bin/bash

echo
echo detecting your environment

if ping -c 1 ix.de &>/dev/null; then
    echo "direct internet connection, doing nothing"
else
    echo "caged environment detected, setting proxy"
    # this is the cntlm proxy, you/we would install
    proxy="http://127.0.0.1:53128"

    export http_proxy=$proxy
    export https_proxy=$proxy
fi

echo
echo Installing latest Flask for rapid iteration

python3 -m venv venv

venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

echo
export port=5000
url=http://localhost:$port
echo now point.ing your browser to $url
echo
which firefox &> /dev/null && sleep 5s && firefox $url &

export FLASK_APP=roulette.py
export FLASK_ENV=development

# removing older sqlite db
rm -f app.db

source venv/bin/activate

flask db upgrade
flask run
