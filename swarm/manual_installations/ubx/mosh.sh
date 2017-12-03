#!/bin/bash
# Mosh Manual Installation
#
# Prereq: apt install libssl-dev pkg-config protobuf-compiler libprotobuf-dev libncurses5-dev

# Testing Prereq
sleep $(shuf -i 10-30 -n 1)
DEBIAN_FRONTEND=noninteractive apt-get install -y libssl-dev pkg-config protobuf-compiler libprotobuf-dev libncurses5-dev

# Normal Procedure
mkdir -p /var/work
cd /var/work
tar xzf /mi/mosh-1.3.2.tar.gz --strip-components=1
./configure
make
make install

sleep $(shuf -i 10-30 -n 1)
## Uninstaller
# cd /var/work
# make uninstall
# rm -rf /var/work

## Testing Uninstaller
# DEBIAN_FRONTEND=noninteractive apt-get autoremove -yq --purge libssl-dev pkg-config protobuf-compiler libprotobuf-dev libncurses5-dev
# cd /var/work
# make uninstall
# rm -rf /var/work
