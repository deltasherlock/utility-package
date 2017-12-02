#!/bin/bash
# Subversion Manual Installation
#
# Prereq: apt install libapr1-dev libaprutil1-dev

mkdir -p /work
cd /work
tar xzf /mi/subversion-1.9.7.tar.gz --strip-components=1
tar xzf /mi/sqlite-amalgamation-3071501.tar.gz
mv sqlite-amalgamation-3071501 sqlite-amalgamation
make
make install

## Uninstaller
# rm -rf /work
# rm -rf /usr/local/include/subversion-1 /usr/local/bin/svn* /usr/local/lib/libsvn* /usr/local/share/man/man1/svn*
