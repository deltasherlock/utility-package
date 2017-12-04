#!/bin/bash
# VSFTPd Manual Installation

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)

# Normal Procedure
mkdir -p /var/work
cd /var/work
tar xzf /mi/vsftpd-3.0.3.tar.gz --strip-components=1
sed -i s/-fPIE/-fPIC/ Makefile
make -s
mkdir -p /usr/local/man/man5
make install

sleep $(shuf -i 10-30 -n 1)

## Uninstaller
# rm -rf /var/work
# rm -rf /usr/local/sbin/vsftpd /usr/local/man/man8/vsftpd.8 /usr/local/man/man5/vsftpd.conf.5
