#!/bin/bash
# p7zip Manual Installation

mkdir -p /var/work
cd /var/work
tar xjf /mi/p7zip_16.02_src_all.tar.bz2 --strip-components=1
make clean
make
make install

## Uninstaller
# rm -rf /var/work
# rm -rf /usr/local/bin/7za /usr/local/man/man1/7z.1 /usr/local/man/man1/7za.1 /usr/local/man/man1/7zr.1 /usr/local/share/doc/p7zip/README /usr/local/share/doc/p7zip/ChangeLog /usr/local/share/doc/p7zip/DOC
