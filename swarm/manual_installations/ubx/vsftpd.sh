#!/bin/bash
# VSFTPd Manual Installation

mkdir -p /work
cd /work
tar xzf /mi/vsftpd-3.0.3.tar.gz --strip-components=1
make
mkdir -p /usr/local/man/man5
make install

## Uninstaller
# rm -rf /work
# rm -rf /usr/local/sbin/vsftpd /usr/local/man/man8/vsftpd.8 /usr/local/man/man5/vsftpd.conf.5
