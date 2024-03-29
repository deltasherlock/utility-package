#!/bin/bash
# Wordpress Manual Installation
#
# Prereqs:
# sudo apt install apache2 mysql-server php php-mysql php-curl php-gd
# To uninstall: rm -rf /var/www/html/*

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 mysql-server php php-mysql php-curl php-gd

# Normal Procedure
WP_DOMAIN="localhost"
WP_ADMIN_USERNAME="admin"
WP_ADMIN_PASSWORD="admin"
WP_ADMIN_EMAIL="no@spam.org"
WP_DB_NAME="wordpress"
WP_DB_USERNAME="wordpress"
WP_DB_PASSWORD="wordpress"
WP_PATH="/var/www/html"
MYSQL_ROOT_PASSWORD="root"

mkdir -p $WP_PATH
cd $WP_PATH
tar xzf /mi/wordpress-4.9.1.tar.gz --strip-components=1

mv wp-config-sample.php wp-config.php
sed -i s/database_name_here/$WP_DB_NAME/ wp-config.php
sed -i s/username_here/$WP_DB_USERNAME/ wp-config.php
sed -i s/password_here/$WP_DB_PASSWORD/ wp-config.php
echo "define('FS_METHOD', 'direct');" >> wp-config.php

chown -R www-data:www-data $WP_PATH

sleep $(shuf -i 10-30 -n 1)

## Testing Uninstaller
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge apache2 mysql-server php php-mysql php-curl php-gd
# rm -rf /var/www/html/*
