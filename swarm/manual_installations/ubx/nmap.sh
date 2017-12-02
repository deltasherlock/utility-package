#!/bin/bash
# Nmap Manual Installation

mkdir -p /work
cd /work
tar xzf /mi/nmap-7.60.tgz --strip-components=1
make
make install

## Uninstaller
# cd /work
# make uninstall
# rm -rf /work
