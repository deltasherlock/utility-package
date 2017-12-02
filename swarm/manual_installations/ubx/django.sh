#!/bin/bash
# Django Manual Installation
#
# Preprereq: make a django virtual env with python 3.5
# Prereq: apt install python-dev
# Prereq: pip install pytz

# Activate python virtual environment
source /root/.virtualenvs/django/bin/activate
cd /var/www/html
tar xzf /mi/django-dev.tar.gz
pip install -e django/
django-admin startproject mysite

## Uninstaller
# source /root/.virtualenvs/django/bin/activate
# pip uninstall django -y
# rm -rf /var/www/html/*
