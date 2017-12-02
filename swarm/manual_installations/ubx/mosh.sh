#!/bin/bash
# Mosh Manual Installation
#
# Prereq: apt install pkg-config protobuf-compiler libprotobuf-dev libncurses5-dev

mkdir -p /work
cd /work
tar xzf /mi/mosh-1.3.2.tar.gz --strip-components=1
./configure
make
make install

## Uninstaller
# cd /work
# make uninstall
# rm -rf /work
