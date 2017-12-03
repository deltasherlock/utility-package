#!/bin/bash
# Wget Manual Installation
#
# Prereq: apt install libgnutls-dev

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y pkg-config libgnutls-dev

mkdir -p /var/work
cd /var/work
tar xzf /mi/wget-1.19.2.tar.gz --strip-components=1
./configure
make
make install

sleep $(shuf -i 10-30 -n 1)

## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge pkg-config libgnutls-dev
