#!/usr/bin/env bash

# Build script for Ubuntu


# Project settings
PROJECT_NAME=hasker
PROJECT_PATH=$(pwd)
SECRET_KEY="$(openssl rand -base64 50)"
CONFIG=${PROJECT_NAME}.config.settings.prod
TZ=Europe/Moscow


# Postgres settings
DB_NAME=${PROJECT_NAME}_db
DB_USER=${PROJECT_NAME}_db_admin
DB_PASSWORD=Hasker1234


echo "1. Try to update/upgrade repositories..."
apt-get -qq -y update
apt-get -qq -y upgrade


echo "2. Try to install required packages..."
ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

PACKAGES=('nginx' 'libpq-dev' 'postgresql' 'python3' 'python3-pip')
for pkg in "${PACKAGES[@]}"
do
    echo "Installing '$pkg'..."
    DEBIAN_FRONTEND=noninteractive
    apt-get install -y ${pkg}
    if [ $? -ne 0 ]; then
        echo "Error installing system packages '$pkg'"
        exit 1
    fi
done


echo "3. Try to install Python3 with project dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/prod.txt
python3 -m pip install uwsgi


echo "4. Try to setup PostgreSQL..."
service postgresql start
su postgres -c "psql -c \"CREATE USER ${DB_USER} PASSWORD '${DB_PASSWORD}'\""
su postgres -c "psql -c \"CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}\""


echo "5. Configure uwsgi..."
mkdir -p /run/uwsgi
mkdir -p /usr/local/etc
mkdir -p /var/log/${PROJECT_NAME}
chown root:nginx /run/uwsgi


cat > /usr/local/etc/uwsgi.ini << EOF
[uwsgi]
chdir = ${PROJECT_PATH}
module = ${PROJECT_NAME}.config.wsgi:application

master = true
processes = 2

socket = /run/uwsgi/${PROJECT_NAME}.sock
chmod-socket = 666

vacuum = true
die-on-term = true

pidfile = /run/uwsgi/${PROJECT_NAME}.pid
logto = /var/log/${PROJECT_NAME}/${PROJECT_NAME}-uwsgi.log

env=DJANGO_SETTINGS_MODULE=${CONFIG}
env=SECRET_KEY=${SECRET_KEY}
env=DB_NAME=${DB_NAME}
env=DB_USER=${DB_USER}
env=DB_PASSWORD=${DB_PASSWORD}
EOF


echo "6. Configure nginx..."
mkdir -p /var/www/static
mkdir -p /var/www/media

cat > /etc/nginx/conf.d/${PROJECT_NAME}.conf << EOF
server {
    listen 80;
    server_name localhost 127.0.0.1;

    access_log /var/log/nginx/$PROJECT_NAME-access.log combined;
    error_log  /var/log/nginx/$PROJECT_NAME-error.log error;

    location /static/ {
        root /var/www;
    }
    location /media/ {
        root /var/www;
    }
    location / {
        uwsgi_pass unix:/run/uwsgi/${PROJECT_NAME}.sock;
        include uwsgi_params;
    }
}
EOF
service nginx restart


echo "6. Prepare Django..."
COMMANDS=('collectstatic' 'makemigrations' 'migrate')
for COMMAND in "${COMMANDS[@]}"
do
    DJANGO_SETTINGS_MODULE=${CONFIG} \
    SECRET_KEY=${SECRET_KEY} \
    DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    python3 manage.py ${COMMAND}
done


echo "8. Start nginx..."
uwsgi --ini /usr/local/etc/uwsgi.ini
