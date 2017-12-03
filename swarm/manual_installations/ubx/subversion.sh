#!/bin/bash
# Subversion Manual Installation
#
# Prereq: apt install libapr1-dev libaprutil1-dev

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y libapr1-dev libaprutil1-dev zlib1g-dev

mkdir -p /var/work
cd /var/work
tar xzf /mi/subversion-1.9.7.tar.gz --strip-components=1
tar xzf /mi/sqlite-amalgamation-3071501.tar.gz
mv sqlite-amalgamation-3071501 sqlite-amalgamation
./configure
make
make install

sleep $(shuf -i 10-30 -n 1)

## Uninstaller
# rm -rf /var/work
# rm -rf /usr/local/include/subversion-1 /usr/local/bin/svn* /usr/local/lib/libsvn* /usr/local/share/man/man1/svn*

## Testing Uninstaller
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge libapr1-dev libaprutil1-dev zlib1g-dev
# rm -rf /var/work
# rm -rf /usr/local/include/subversion-1 /usr/local/bin/svn* /usr/local/lib/libsvn* /usr/local/share/man/man1/svn*
