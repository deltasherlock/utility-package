#!/bin/bash
# DeltaSherlock Swarm Member Bootstrap Script
# For CentOS 7
# Run this immediately after boot

# Fix any broken packages that may have arisen from a previous reboot
yum-complete-transaction -y
package-cleanup --cleandupes -y

cd /root/utility-package/swarm

# Remove any lingering packages from the list
yum remove -C -y --setopt=clean_requirements_on_remove=0 $(grep -vE "^\s*#" repo_packages_centos.lst  | tr "\n" " ")

# Update source code
git pull

# Activate python virtual environment
source /root/.virtualenvs/ds/bin/activate

# Hand off to the python init script
python /root/utility-package/swarm/worker_init.py
