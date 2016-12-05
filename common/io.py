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
from base64 import b64encode,b64decode

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
