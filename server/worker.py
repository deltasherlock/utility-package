"""
Contains methods to be executed via an RQ queue
"""
import pickle
from deltasherlock.common.io import DSDecoder
from deltasherlock.common.fingerprinting import Fingerprint
from deltasherlock.server.learning import MLModel, MLAlgorithm

def process_fingerprint(fingerprint_json_str: str, endpoint_url: str, parameters: dict) -> list:
    #Basically, we have to load the model from file and predict against it
    fingerprint = DSDecoder().decode(fingerprint_json_str)
    model_path = "/tmp/DS_MLModel" #+ str(int(fingerprint.method))
    model = pickle.load(open(model_path, "rb"))

    #TODO notify the endpoint IP!

    return model.predict(fingerprint)
