"""
Contains methods to be executed via an RQ queue
"""


def install_eventlabel(eventlabel_dict: dict):
    """
    Executes the install_script within an EventLabel while recording a changeset

    :param eventlabel_dict: the EventLabel.__dict__ of the EventLabel to be installed
    """
    import os
    import stat
    import subprocess
    from time import time
    from platform import linux_distribution
    from tempfile import NamedTemporaryFile
    from deltasherlock.client import networking
    from deltasherlock.client.ds_watchdog import DeltaSherlockWatchdog

    install_log = "----Event " + eventlabel_dict['name'] + " started at " + str(time()) + "----\n"
    # TODO: make this a setting?

    if linux_distribution()[0] == "Ubuntu":
        watch_paths = ["/bin/", "/boot/", "/etc/", "/lib/", "/lib64/", "/opt/",
                       "/run/", "/sbin/", "/snap/", "/srv/", "/usr/", "/var/"]
    else:
        watch_paths = ["/bin/", "/boot/", "/etc/", "/lib/", "/lib64/", "/opt/",
                       "/run/", "/sbin/", "/srv/", "/usr/", "/var/"]

    with NamedTemporaryFile(mode='w', delete=False) as tempf:
        # Save the install script to a tmp file
        print(eventlabel_dict['install_script'], file=tempf)
        # Change the temp file to make it executable
        os.fchmod(tempf.fileno(), stat.S_IRUSR | stat.S_IEXEC)
        fname = tempf.name

    # Begin recording by instantiating the watchdog
    os.sync()
    dswd = DeltaSherlockWatchdog(watch_paths)

    # Run the command!
    install_result = subprocess.run(args="bash " + fname,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

    # Now eject the changeset and stop the watchdog
    changeset = dswd.mark()
    del dswd

    # Delete the tmp file
    os.remove(fname)

    # Append some information
    install_log += install_result.stdout.decode("utf-8")
    install_log += "\n---Event returned code " + \
        str(install_result.returncode) + " at " + str(time()) + "----"

    # Make sure this install was successful
    if "E: Could not get lock /" in install_log or "0 upgraded, 0 newly installed, 0 to remove" in install_log or "Error: Nothing to do" in install_log or "already installed and latest version" in install_log:
        install_log += "\nError detected."
        networking.swarm_submit_log(install_log, log_type="ER")
        raise Exception("Installation failed due to apt/yum")

    # Add the id of this event label as a regular changeset label
    changeset.add_label(eventlabel_dict['id'])

    # Now submit the changeset to the API
    cs_req = networking.swarm_submit_changeset(changeset)

    # Now submit the swarm member log to the API
    networking.swarm_submit_log(install_log, cs_req.json()['url'])


def install_eventlabel_unsupervised(eventlabel_dict: dict):
    """
    Executes the install_script within an EventLabel without caring about recording

    :param eventlabel_dict: the EventLabel.__dict__ of the EventLabel to be installed
    """
    import os
    import stat
    import subprocess
    from time import time
    from tempfile import NamedTemporaryFile
    from deltasherlock.client import networking

    install_log = "----Event " + eventlabel_dict['name'] + " started at " + str(time()) + "----\n"

    with NamedTemporaryFile(mode='w', delete=False) as tempf:
        # Save the install script to a tmp file
        print(eventlabel_dict['install_script'], file=tempf)
        # Change the temp file to make it executable
        os.fchmod(tempf.fileno(), stat.S_IRUSR | stat.S_IEXEC)
        fname = tempf.name

    os.sync()

    # Run the command!
    install_result = subprocess.run(args="bash " + fname,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

    # Delete the tmp file
    os.remove(fname)

    # Append some information
    install_log += install_result.stdout.decode("utf-8")
    install_log += "\n---Event returned code " + \
        str(install_result.returncode) + " at " + str(time()) + "----"

    # Make sure this install was successful
    if "E: Could not get lock /" in install_log:
        install_log += "\nError detected."
        networking.swarm_submit_log(install_log, log_type="ER")
        raise Exception("Installation failed due to apt lock")
    elif "Error: Nothing to do" in install_log:
        install_log += "\nError detected."
        networking.swarm_submit_log(install_log, log_type="ER")
        raise Exception("Installation failed due to yum")

    # Now submit the swarm member log to the API
    try:
        networking.swarm_submit_log(install_log)
    except:
        # Unsupervised tasks aren't actually that important, so if the log post fails
        # it's nbd
        pass


def process_fingerprint(fingerprint_json_str: str, endpoint_url: str, client_ip: str, parameters: dict, django_params: dict = None) -> list:
    """
    Accepts fingerprints from the API and produces a prediction
    """
    import pickle
    from time import time
    from deltasherlock.common.io import DSDecoder
    from deltasherlock.common.fingerprinting import Fingerprint
    from deltasherlock.server.learning import MLModel, MLAlgorithm

    error = None
    start_time = time()
    queue_item_id = "[no associated QueueItem]"
    queue_item_submission_time = "[no associated QueueItem]"

    # First, dial into Django to update our QueueItem to the Running state
    if django_params is not None:
        import os
        import sys
        import django
        from rq import get_current_job
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              django_params['settings_module'])
        sys.path.append(django_params['proj_path'])
        os.chdir(django_params['proj_path'])
        django.setup()
        from deltasherlock_server.models import QueueItem

        # Now we have access to the database, so get the QueueItem
        q = QueueItem.objects.get(rq_id=get_current_job().id)
        q.rq_running()
        queue_item_id = q.id
        queue_item_submission_time = q.submission_time.timestamp()

    # Basically, we have to load the model from file and predict against it
    fingerprint = DSDecoder().decode(fingerprint_json_str)
    model_path = "/tmp/DS_MLModel"  # + str(int(fingerprint.method))
    model = pickle.load(open(model_path, "rb"))

    prediction = model.predict(fingerprint)

    # TODO notify the endpoint IP!
    if endpoint_url is not None:
        import re
        # Borrowed from Django's URLValidator
        urlregex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        # If url is valid
        if urlregex.fullmatch(endpoint_url) is not None:

            from requests import post
            post_data = {'queue_id': queue_item_id,
                         'submission_time': queue_item_submission_time,
                         'start_time': start_time,
                         'done_time': time(),
                         'client_ip': client_ip,
                         'prediction': prediction}
            try:
                post(endpoint_url, json=post_data)
            except:
                print("Error: Could not connect to endpoint_url")
                error = "Failed to connect to endpoint_url"
        else:
            print("Error: Invalid endpoint_url")
            error = "Invalid endpoint_url"

    print(str(prediction))

    # Now we have to dial back into Django to update the database
    if django_params is not None:
        q.rq_complete(labels=prediction, error=error)

    return(prediction)
