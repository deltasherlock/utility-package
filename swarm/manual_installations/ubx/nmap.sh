#!/bin/bash
# Nmap Manual Installation

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)

mkdir -p /var/work
cd /var/work
tar xzf /mi/nmap-7.60.tgz --strip-components=1
./configure
make -s
make install

sleep $(shuf -i 10-30 -n 1)

## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work
