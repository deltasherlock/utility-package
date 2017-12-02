#!/bin/bash
# Wget Manual Installation
#
# Prereq: apt install libgnutls-dev

mkdir -p /work
cd /work
tar xzf /mi/wget-1.19.2.tar.gz --strip-components=1
./configure
make
make install

## Uninstaller
# cd /work
# make uninstall
# rm -rf /work
