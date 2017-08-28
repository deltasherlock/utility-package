# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock client networking module. Contains methods for communicating with
a DeltaSherlock server.
"""
from socket import gethostname, socket, AF_INET, SOCK_DGRAM
from requests import Response, post, get, patch, codes
from deltasherlock.common.io import DSEncoder
from deltasherlock.common.changesets import Changeset
from deltasherlock.common.fingerprinting import Fingerprint

# Do not include trailing slash
SERVER_URL = "http://api.v-m.tech:8000"

METADATA_URLS = ["http://169.254.169.254/2009-04-04/meta-data/member-url", #OpenStack
                 "http://metadata.google.internal/computeMetadata/v1/instance/"] #GCE


def submit_fingerprint(fingerprint: Fingerprint, endpoint_url: str, parameters: str) -> Response:
    """
    Submit a fingerprint to a DeltaSherlock server for processing

    :param fingerprint: the Fingerprint object to be submitted
    :param endpoint_url: the full URL that the server should request upon completion
    :param paramaters: a custom parameter string to be provided to the server
    :returns: a Requests.Response object representing the completed query

    """
    data = {'fingerprint': DSEncoder().encode(fingerprint),
            'endpoint_url': endpoint_url,
            'parameters': parameters}
    return post(SERVER_URL + "/fingerprint/submit/", json=data)

def get_member_url() -> str:
    """
    Returns the API URL representing this instance
    """
    # First, figure out what URL to contact
    # Check if it's stored in the filesystem
    try:
        with open("/member-url", "r") as f:
            return f.readline().strip()
    except:
        # File probably doesn't exist. Let's try the metadata method
        # Try different urls since we don't know what cloud we're in
        for url in METADATA_URLS:
            try:
                req = get(url, headers={'Metadata-Flavor': 'Google'})
                if req.status_code == codes.ok:
                    # Break as soon as we get a working URL
                    break
            except:
                # Don't do anything, just move to the next URL
                pass
        # Check to make sure we escaped that loop with a working URL
        if req.status_code == codes.ok:
            # Save that for next time
            with open("/member-url", "w") as f:
                print(req.text, file=f)
            return req.text
        else:
            # TODO: throw an error
            return

def swarm_checkin() -> list:
    """
    Runs immediately after boot to let the server know we're ready to accept tasks.
    If successful, the server will reply with a list of RQ queues to attach to

    :returns: a list of RQ queue names to attach to
    """

    # Figure out our internal IP (https://stackoverflow.com/a/166589)
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        int_ip = s.getsockname()[0]

    # Now that we have our IP and  correct check-in url, make the request!
    checkin_url = SERVER_URL + get_member_url()
    req = patch(url=checkin_url, json={'ip': int_ip, 'status': 'RN'})

    return req.json()["attached_rq_queues"]


def swarm_submit_changeset(changeset: Changeset) -> Response:
    """
    Submit a Changeset to a DeltaSherlock server for storage in the changeset
    database. Submitted changeset must correspond to at least one EventLabel in
    the database

    :param changeset: the Changeset object to be submitted
    :param eventlabel_ids: a collection of integers representing the primary
    keys of the EventLabels that are present in this changeset
    :returns: a Requests.Response object representing the completed query
    """
    data = {'changeset': DSEncoder().encode(changeset)}
    return post(SERVER_URL + "/swarm/changeset/", json=data)


def swarm_submit_log(log: str, resulting_changeset_url: str = None, log_type: str = "IN") -> Response:
    """
    Submit a SwarmMemberLog to a DeltaSherlock server for record-keeping

    :param log: a string containing the log
    :param resulting_changeset_id: the database ID of the changeset produced by
    the events that occured within this log (optional)
    :returns: a Requests.Response object representing the completed query
    """
    data = {'member': SERVER_URL + get_member_url(),
            'log': log,
            'resulting_changeset': resulting_changeset_url,
            'log_type': log_type}
    return post(SERVER_URL + "/swarm/log/", json=data)
