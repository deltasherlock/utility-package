#!/bin/bash
# Django Manual Installation
#
# Preprereq: make a django virtual env with python 3.5
# Prereq: pip install pytz

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
mkdir -p /var/work
cd /var/work
virtualenv django -p /usr/bin/python3
source /var/work/django/bin/activate
pip install pytz

# For training: Activate python virtual environment
# source /root/.virtualenvs/django/bin/activate
mkdir -p /var/www/html
cd /var/www/html
tar xzf /mi/django-dev.tar.gz
pip install -e django/
django-admin startproject mysite

sleep $(shuf -i 10-30 -n 1)

## Training Uninstaller
# source /root/.virtualenvs/django/bin/activate
# pip uninstall django -y
# rm -rf /var/www/html/*

## Testing Uninstaller
# rm -rf /var/work
# rm -rf /var/www/html/*
