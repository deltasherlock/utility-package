"""
DeltaSherlock Client Quick Submission Test

Creates a changeset and fingerprint from some random filesystem activity, then
submits to server
"""
# pylint: disable=C0103
import time
import tempfile
from deltasherlock.client import networking as net
from deltasherlock.common import fingerprinting as fp
from deltasherlock.common import dictionaries as dc
from deltasherlock.client.ds_watchdog import DeltaSherlockWatchdog
from deltasherlock.server import learning as lrn
from deltasherlock.common.io import random_activity, uid


testdirpath = tempfile.mkdtemp(suffix=str(uid()))
print("Created test directory " + testdirpath)

watch_paths = [testdirpath, "/var/", "/bin/", "/usr/", "/etc/"]

print("Creating DeltaSherlockWatchdog...")
dswd = DeltaSherlockWatchdog(watch_paths, "*", ".")

changesets = []
all_neighbor_sentences = []
all_filetree_sentences = []

for i in range(3):
    print("Creating some file activity...")
    time.sleep(1)
    random_activity(testdirpath)
    time.sleep(1)
    print("Marking CS" + str(i))
    cs = dswd.mark()
    cs.add_label("Changeset" + str(i))
    all_neighbor_sentences += cs.get_neighbor_sentences()
    all_filetree_sentences += cs.get_filetree_sentences()
    changesets.append(cs)

print("Creating neighbor dictionary...")

myNDict = dc.create_dictionary(all_neighbor_sentences, threads=1)

print("Creating filetree dictionary...")
myFTDict = dc.create_dictionary(all_filetree_sentences, threads=1)

print("Creating combined fingerprints")
fingerprints = []
for cs in changesets:
    fingerprints.append(fp.changeset_to_fingerprint(cs, fp.FingerprintingMethod.combined,
                                                    filetree_dictionary=myFTDict,
                                                    neighbor_dictionary=myNDict))

print("Printing predicted quantities")
for fprint in fingerprints:
    print(str(fprint.predicted_quantity))

print("Creating a machine learning model from the combine FP")
myMLModel = lrn.MLModel(fingerprints, lrn.MLAlgorithm.decision_tree)

print("Testing recognition of Changeset1")
print(str(myMLModel.predict(fingerprints[1])))

print("-------BEGIN API TESTING-------")
print("Ensure Redis Server and RQ worker are running")
import requests
import pickle
print("Saving model to /tmp/DS_MLModel")
pickle.dump(myMLModel, open("/tmp/DS_MLModel", mode='wb'))

print("Submitting myCombinedFP1 to API")
res = net.submit_fingerprint(
    fingerprints[1], "http://endpoint.url/", "no_params")
print("Here's what the POST Request looked like")
req = res.request
print('{}\n{}\n{}\n\n{}'.format(
    '-----------START-----------',
    req.method + ' ' + req.url,
    '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
    req.body,
))
print("------------END------------")
print("And here's the server's response. (Will contain the job ID if successful)")
print(str(res.status_code) + ": " + res.text)

print("All done!")

print("Destroying Client Watchdog")
del dswd
