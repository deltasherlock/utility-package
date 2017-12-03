#!/bin/bash
# LigHTTPd Manual Installation

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y zlib1g-dev

# Normal Procedure
mkdir -p /var/work
cd /var/work
tar xzf /mi/lighttpd-1.4.48.tar.gz --strip-components=1
./configure --without-pcre --without-bzip2
make
make install

sleep $(shuf -i 10-30 -n 1)

## Training Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work

## Testing Uninstaller
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge zlib1g-dev
# cd /var/work
# make uninstall
# rm -rf /var/work
