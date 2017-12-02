#!/bin/bash
# Hadoop Manual Installation
#
# Prereq: sudo apt install openjdk-8-jre
#

addgroup hadoop
adduser --disabled-password --gecos "" --ingroup hadoop hduser

mkdir -p /usr/local/hadoop
cd /usr/local/hadoop
tar xzf /mi/hadoop-2.9.0.tar.gz --strip-components=1

## Uninstaller
# deluser hduser --remove-home
# delgroup hadoop
# rm -rf /usr/local/hadoop
