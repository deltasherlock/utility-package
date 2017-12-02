#!/bin/bash
# LigHTTPd Manual Installation

mkdir -p /var/work
cd /var/work
tar xzf /mi/lighttpd-1.4.48.tar.gz --strip-components=1
./configure --without-pcre --without-bzip2
make
make install

## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work
