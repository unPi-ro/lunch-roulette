#!/bin/bash

do=""
proxy=""

echo
echo detecting your environment

if ping -c 1 ix.de &>/dev/null; then
    echo "direct internet connection, doing nothing"
else
    echo "caged environment detected, setting proxy"
    # this is the cntlm proxy, you/we would install
    proxy="http://127.0.0.1:53128"
fi

# just another guard before running yum commands
if [ -n "$proxy" -a -f /etc/centos-release ]; then
    echo
    echo "you must be in an office, right?"
    echo
    echo "get ready to rock on your Flask!"
    echo
    git config --global credential.helper "cache --timeout=$(( 8*3600 ))"
    git config --global http.proxy $proxy
    rpms=""
    echo "in office we need sudo to build & run our stack"
    echo
    echo "lets cache the sudo credentials now"
    export do="sudo"
    $do pwd
    rpms="$rpms python36-virtualenv.noarch python36-pip"
    which cntlm &>/dev/null || rpms="$rpms cntlm"
    which redis-cli &>/dev/null || rpms="$rpms redis"
    rpms="$rpms postgresql postgresql-server pgadmin3"
    [ -n "$rpms" ] && echo "installing for you $rpms"
    [ -n "$rpms" ] && $do yum install -y $rpms
    $do systemctl enable cntlm
    $do systemctl enable redis
    $do systemctl enable postgresql
    echo
    echo configuring cntlm
    if [ ! -f ~/cntlm.ini ]; then
        cat cntlm.ini.head > ~/cntlm.ini
        read -p "please type your Windows/DOMAIN username: " aduser
        echo -n "creating cntlm hashes for your DOMAIN account, please type your Windows password: "
        cntlm -H -u $aduser -d your.DOMAIN | \
          sed -e "s/Password:/Username \t$aduser/" | $do tee -a ~/cntlm.ini
    else
        echo your local cntlm.ini is already created, using it
    fi
    $do sed -i "s/cntlm.conf/cntlm.ini/" /usr/lib/systemd/system/cntlm.service
    $do ln -sf ~/cntlm.ini /etc/cntlm.ini
    echo
    $do systemctl daemon-reload && echo restarted systemctl daemon
    $do systemctl restart cntlm && echo restarted cntlm
    $do systemctl restart redis && echo restarted redis
    echo
    echo initdb the postgresql, if needed
    $do postgresql-setup initdb &> /dev/null
    $do systemctl restart postgresql && echo restarted postgresql
    echo
    echo creating the required postgresql databases, if needed
    $do -iu postgres createuser --superuser $USER &> /dev/null
    $do -iu postgres createdb lunch &> /dev/null
fi

echo
echo running ./local/install.sh
./local/install.sh
