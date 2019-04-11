#!/usr/bin/env bash

echo "0. Initialization system dependencies..."

apt-get -qq -y update
apt-get -qq -y upgrade
apt-get install -y git \
                   make \
                   gcc \
                   vim \
                   openssl \
