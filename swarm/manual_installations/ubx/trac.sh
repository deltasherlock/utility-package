#!/bin/bash
# Trac Manual Installation
#
# Preprereq: make a trac virtual env with python 2.7
# Prereq: apt install python-dev mysql-server libmysqlclient-dev
# Prereq: pip install genshi mysql-python

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y python-dev mysql-server libmysqlclient-dev
mkdir -p /var/work
cd /var/work
virtualenv trac
source /var/work/trac/bin/activate
pip install genshi mysql-python

# Training: Activate python virtual environment
#source /root/.virtualenvs/trac/bin/activate

pip install trac
cd /var/www/html
trac-admin testtrac initenv "Test" "sqlite:db/trac.db"

sleep $(shuf -i 10-30 -n 1)

## Uninstaller
# source /root/.virtualenvs/trac/bin/activate
# pip uninstall trac -y
# rm -rf /var/www/html/testtrac

## Testing Uninstaller
# rm -rf /var/www/html/testtrac
# rm -rf /var/work
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge python-dev mysql-server libmysqlclient-dev
