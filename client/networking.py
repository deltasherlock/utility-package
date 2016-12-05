# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock client networking module. Contains methods for communicating with
a DeltaSherlock server.
"""
from deltasherlock.common.io import object_to_base64
from deltasherlock.common.fingerprinting import Fingerprint
from requests import Response, post

#Do not include trailing slash
SERVER_URL = "http://127.0.0.1:8000"

def submit_fingerprint(fingerprint: Fingerprint) -> Response:
    data = { "fingerprint" : object_to_base64(fingerprint) }
    return post(SERVER_URL+"/fingerprint/submit", data=data)
