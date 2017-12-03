#!/bin/bash
# Hadoop Manual Installation
#
# Prereq: sudo apt install openjdk-8-jre
#

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jre

# Normal Procedure
addgroup hadoop
adduser --disabled-password --gecos "" --ingroup hadoop hduser

mkdir -p /usr/local/hadoop
cd /usr/local/hadoop
tar xzf /mi/hadoop-2.9.0.tar.gz --strip-components=1

sleep $(shuf -i 10-30 -n 1)

## Training Uninstaller
# deluser hduser --remove-home
# delgroup hadoop
# rm -rf /usr/local/hadoop


## Testing Uninstaller
# deluser hduser --remove-home
# delgroup hadoop
# rm -rf /usr/local/hadoop
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge openjdk-8-jre
