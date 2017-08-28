#!/bin/bash
# DeltaSherlock Swarm Member Bootstrap Script
# For Ubuntu/Debian
# Run this immediately after boot

# Fix any broken packages that may have arisen from a previous reboot
rm /var/lib/apt/lists/lock
rm /var/cache/apt/archives/lock
apt-get update --fix-missing
dpkg --configure -a
apt-get install -f

cd /root/utility-package/swarm

# Remove any lingering packages from the list
apt-get remove --purge $(grep -vE "^\s*#" repo_packages_ubuntu.lst  | tr "\n" " ")

# Update source code
git pull

# Activate python virtual environment
source /root/.virtualenvs/ds/bin/activate

# Hand off to the python init script
python /root/utility-package/swarm/worker_init.py