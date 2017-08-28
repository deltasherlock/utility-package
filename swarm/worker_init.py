#!/usr/bin/env python
"""
DeltaSherlock Swarm Member Initialization Script

Launched by a shell script after updating source code. Prepares the instance to
accept tasks
"""
from time import time
from subprocess import run
from socket import gethostname
from deltasherlock.client import networking

# First, check-in with the server and get the names of the RQ queues we need
queues = networking.swarm_checkin()

# Log a notification back to the server
log = gethostname() + " successfully booted and checked-in at " + str(time())
networking.swarm_submit_log(log=log, log_type='NT')

# Now launch the RQ workers
log = gethostname() + " attached RQ workers to the following queues:\n"
log_type = 'NT'
for queue in queues:
    run_res = run("rq worker --url http://redis.v-m.tech:6379 " + queue + " &", shell=True)
    log += queue + " at " + str(time()) + " (RC: " + str(run_res.returncode) + ")\n"

    if run_res.returncode != 0:
        log_type = 'ER'

# Submit one more log
networking.swarm_submit_log(log=log, log_type=log_type)
