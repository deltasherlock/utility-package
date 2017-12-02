#!/bin/bash
# Trac Manual Installation
#
# Preprereq: make a trac virtual env with python 2.7
# Prereq: apt install python-dev mysql-server libmysqlclient-dev
# Prereq: pip install genshi mysql-python

# Activate python virtual environment
source /root/.virtualenvs/trac/bin/activate

pip install trac
cd /var/www/html
trac-admin testtrac initenv "Test" "sqlite:db/trac.db"

## Uninstaller
# source /root/.virtualenvs/trac/bin/activate
# pip uninstall trac -y
# rm -rf /var/www/html/testtrac
