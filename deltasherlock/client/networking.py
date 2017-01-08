# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock client networking module. Contains methods for communicating with
a DeltaSherlock server.
"""
from deltasherlock.common.io import DSEncoder
from deltasherlock.common.fingerprinting import Fingerprint
from requests import Response, post

# Do not include trailing slash
SERVER_URL = "http://127.0.0.1:8000"


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
    return post(SERVER_URL + "/fingerprint/submit/", data=data)
