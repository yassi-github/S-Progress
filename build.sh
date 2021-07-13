#!/bin/bash

cd docker_conf/nginx/ssl
openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -subj /CN=localhost -keyout server.key -out server.crt
# openssl genrsa 2024 > server.key
# openssl req -new -key server.key > server.csr
# openssl x509 -req -days 3650 -signkey server.key < server.csr > server.crt
chown `echo $USER` .

sudo -u $USER docker-compose up -d
# docker-compose ps -a
