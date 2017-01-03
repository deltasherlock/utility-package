# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock common IO module. Useful for saving and loading fingerprint/changeset objects
"""
import pickle
import os
import tempfile
import random
import string
import time
import json
import numpy as np
from base64 import b64encode,b64decode
from deltasherlock.common.changesets import Changeset
from deltasherlock.common.changesets import ChangesetRecord
from deltasherlock.common.fingerprinting import Fingerprint
from deltasherlock.common.fingerprinting import FingerprintingMethod

def object_to_base64(obj: object) -> str:
    """
    Converts any Pickle-able object to a base64 endcoded string. Good for transport
    via network
    """
    return b64encode(pickle.dumps(obj)).decode('UTF-8')

def base64_to_object(b64_string: str) -> object:
    """
    Converts the result of object_to_base64 back to an object.
    """
    return pickle.loads(b64decode(b64_string))

def save_object_as_base64(obj: object, save_path: str):
    """
    Basically saves a text representation of any Pickle-able object to a file.
    Although less space efficient than a regular binary Pickle file, it allows for
    easier transport via network
    """
    with open(save_path, 'w') as output_file:
        print(object_to_base64(obj), file=output_file)

def load_object_from_base64(load_path: str) -> object:
    """
    Load a file created by save_object_as_base64()
    """
    with open(load_path, 'r') as input_file:
        return base64_to_object(input_file.read().replace('\n', ''))

def uid(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Generates a nice short unique ID for random files. For testing
    """
    return ''.join(random.choice(chars) for _ in range(size))

def random_activity(testdirpath):
    """
    Create some random file system activity in a certain folder. For testing
    """
    files_created = []
    for i in range(10):
        files_created.append(tempfile.mkstemp(dir=testdirpath, suffix=str(uid())))
    testsubdirpath = os.path.join(testdirpath, str(uid()))
    os.mkdir(testsubdirpath)
    time.sleep(2)
    for i in range(15):
        files_created.append(tempfile.mkstemp(dir=testsubdirpath, suffix=str(uid())))
    time.sleep(2)

    return files_created

class DSEncoder(json.JSONEncoder):
    """
    Provides some JSON serialization facilities for custom objects used by
    DeltaSherlock (mainly changesets and fingerprints)
    """

    def default(self, o: object):
        """
        Coverts a given object into a JSON serializable object

        :param: o the Fingerprint or Changeset to be serialized
        :returns: a JSON serializable object to be processed by the standard Python
        JSON encoder
        """
        serializable = dict()
        # Check what kind of object o is
        if (isinstance(o, Fingerprint)):
            serializable['type'] = "Fingerprint"
            serializable['method'] = o.method.value
            serializable['labels'] = o.labels
            serialziable['predicted_quantity'] = o.predicted_quantity
            serializable['array'] = o.tolist()

        elif (isinstance(o, Changeset)):
            serializable['type'] = "Changeset"
            serializable['open_time'] = o.open_time
            serializable['open'] = o.open
            serializable['close_time'] = o.close_time
            serializable['labels'] = o.labels
            serializable['predicted_quantity'] = o.predicted_quantity

            #Rescursively serialize the file change lists
            serializable['creations'] = list()
            for cs_record in o.creations:
                serializable['creations'].append(default(cs_record))

            serializable['modifications'] = list()
            for cs_record in o.modifications:
                serializable['modifications'].append(default(cs_record))

            serializable['deletions'] = list()
            for cs_record in o.deletions:
                serializable['deletions'].append(default(cs_record))

        elif (isinstance(o, ChangesetRecord)):
            serializable['type'] = "ChangesetRecord"
            serializable['filename'] = o.filename
            serializable['mtime'] = o.mtime
            serializable['neighbors'] = o.neighbors

        else:
            # Unknown object. Pass it up to the parent encoder
            serializable = json.JSONEncoder.default(self, o)

        return serializable

class DSDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: dict):
        """
        Called in order to covert a newly-deserialized list back to a usable
        object

        :param: obj the newly-deserialized list
        :returns: the corresponding DeltaSherlock object
        """
        deserialized = None
        import ipdb; ipdb.set_trace()
        if obj['type'] == "Fingerprint":
            deserialized = Fingerprint(np.array(obj['array']))
            deserialized.method = FingerprintingMethod(obj.method)
            deserialized.labels = obj['labels']
            deserialized.predicted_quantity = obj['predicted_quantity']

        elif obj['type'] == "Changeset":
            deserialized = Changeset(obj['open_time'])
            deserialized.open = obj['open']
            deserialized.close_time = obj['close_time']
            deserialized.labels = obj['labels']
            deserialized.predicted_quantity = obj['predicted_quantity']

            deserialized.creations = list()
            for cs_record_ser in obj['creations']:
                deserialized.creations.append(object_hook(cs_record_ser))

            deserialized.modifications = list()
            for cs_record_ser in obj['modifications']:
                deserialized.modifications.append(object_hook(cs_record_ser))

            deserialized.deletions = list()
            for cs_record_ser in obj['deletions']:
                deserialized.deletions.append(object_hook(cs_record_ser))

        elif obj['type'] == "ChangesetRecord":
            deserialized = ChangesetRecord(obj['filename'], obj['mtime'], obj['neighbors'])

        else:
            #Give up
            raise ValueError("Unable to determine type of JSON object")

        return deserialized
