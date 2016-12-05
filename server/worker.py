"""
Contains methods to be executed via an RQ queue
"""
import pickle
from deltasherlock.common.io import base64_to_object
from deltasherlock.common.fingerprinting import Fingerprint
from deltasherlock.server.learning import MLModel, MLAlgorithm

def process_fingerprint(fingerprint_b64_str: str, parameters: dict, endpoint_url: str) -> list:
    #Basically, we have to load the model from file and predict against it
    fingerprint = base64_to_object(fingerprint_b64_str)
    model_path = "/tmp/DS_MLModel" #+ str(int(fingerprint.method))
    model = pickle.load(open(model_path, "rb"))

    #TODO notify the endpoint IP!

    return model.predict(fingerprint)
