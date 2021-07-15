#!/bin/bash

docker build -t alpine-cmd alpine-cmd

cd docker_conf/nginx/ssl
openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -subj /CN=localhost -keyout server.key -out server.crt
chown `echo $USER` .
cd ../../..
sudo -u $USER env PWD=$(pwd) docker-compose up --build
# docker-compose ps -a
docker-compose exec db psql spro < spro_v2.sql
