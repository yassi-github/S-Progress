#!/bin/bash

set -xe

docker build -t alpine-cmd alpine-cmd

mkdir -p docker_conf/nginx/ssl
mkdir -p answer/script_files
cd docker_conf/nginx/ssl
openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -subj /CN=localhost -keyout server.key -out server.crt
chown $USER .
cd ../../..

set +e

which docker-compose >/dev/null 2>&1
if [[ $? == 1 ]]
then
    docker compose >/dev/null 2>&1
    if [[ $? == 1 ]]
    then
        echo -e "Please install docker-compose !\nAborting..."
        exit 1
    else
        set -e
        
        sudo -u $USER env PWD=$(pwd) docker compose up -d --build
        docker compose exec -T db psql spro < spro.sql

        exit $?
    fi
fi

set -e

sudo -u $USER env PWD=$(pwd) docker-compose up -d --build
docker-compose exec -T db psql spro < spro.sql
