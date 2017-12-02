#!/bin/bash
# Nmap Manual Installation

mkdir -p /var/work
cd /var/work
tar xzf /mi/nmap-7.60.tgz --strip-components=1
make
make install

## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work
