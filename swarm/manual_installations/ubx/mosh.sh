#!/bin/bash
# Mosh Manual Installation
#
# Prereq: apt install pkg-config protobuf-compiler libprotobuf-dev libncurses5-dev

mkdir -p /var/work
cd /var/work
tar xzf /mi/mosh-1.3.2.tar.gz --strip-components=1
./configure
make
make install

## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work
