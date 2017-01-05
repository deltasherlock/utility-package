"""
DeltaSherlock Client Scanning Test

Demonstrates the creation of a changeset and fingerprint from some random
filesystem activity
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

print("Creating some file activity...")
time.sleep(5)
random_activity(testdirpath)
time.sleep(5)
print("Marking CS1...")
testcs1 = dswd.mark()

print("Creating some more file activity...")
time.sleep(5)
random_activity(testdirpath)
time.sleep(5)

print("Marking CS2...")
testcs2 = dswd.mark()

print("Creating EVEN more file activity...")
time.sleep(5)
random_activity(testdirpath)
time.sleep(5)

print("Marking CS3...")
testcs3 = dswd.mark()

time.sleep(5)
print("Breaking... Feel free to install something now")
import ipdb
ipdb.set_trace()
time.sleep(5)
print("Marking CSU...")
testcsU = dswd.mark()

# print("Printing neighbor sentences...")
# print(testcs.get_neighbor_sentences())
#
# print("Printing filetree sentences...")
# print(testcs.get_filetree_sentences())

testcs1.add_label("Changeset1")
testcs2.add_label("Changeset2")
testcs3.add_label("Changeset3")
testcsU.add_label("ChangesetU")

print("Creating neighbor dictionary...")

all_neighbor_sentences = testcs1.get_neighbor_sentences() + testcs2.get_neighbor_sentences() + \
    testcs3.get_neighbor_sentences() + testcsU.get_neighbor_sentences()

myNDict = dc.create_dictionary(all_neighbor_sentences, threads=1)

print("Creating filetree dictionary...")
all_filetree_sentences = testcs1.get_filetree_sentences() + testcs2.get_filetree_sentences() + \
    testcs3.get_filetree_sentences() + testcsU.get_filetree_sentences()
myFTDict = dc.create_dictionary(all_filetree_sentences, threads=1)

#print("Trying neighbor sanity check...")
#print(myNDict.doesnt_match("tmp tmpi".split()))

#print("Trying filetree sanity check...")
#print(myFTDict.doesnt_match("tmp tmpi".split()))

# print("Destroying Client Watchdog")
# del dswd

print("Creating a histogram fingerprint")
myHistogramFP1 = fp.changeset_to_fingerprint(
    testcs1, fp.FingerprintingMethod.histogram)
myHistogramFP2 = fp.changeset_to_fingerprint(
    testcs2, fp.FingerprintingMethod.histogram)
myHistogramFP3 = fp.changeset_to_fingerprint(
    testcs3, fp.FingerprintingMethod.histogram)
myHistogramFPU = fp.changeset_to_fingerprint(
    testcsU, fp.FingerprintingMethod.histogram)

# print("Printing that...")
# print(myHistogramFP)
# print(str(len(myHistogramFP)))

print("Creating a combined fingerprint")
myCombinedFP1 = fp.changeset_to_fingerprint(testcs1, fp.FingerprintingMethod.combined,
                                            filetree_dictionary=myFTDict,
                                            neighbor_dictionary=myNDict)
myCombinedFP2 = fp.changeset_to_fingerprint(testcs2, fp.FingerprintingMethod.combined,
                                            filetree_dictionary=myFTDict,
                                            neighbor_dictionary=myNDict)
myCombinedFP3 = fp.changeset_to_fingerprint(testcs3, fp.FingerprintingMethod.combined,
                                            filetree_dictionary=myFTDict,
                                            neighbor_dictionary=myNDict)
myCombinedFPU = fp.changeset_to_fingerprint(testcsU, fp.FingerprintingMethod.combined,
                                            filetree_dictionary=myFTDict,
                                            neighbor_dictionary=myNDict)

# print("Printing that...")
# print(myCombinedFP)
#print("Printing labels in FP")
# print(str(myCombinedFP.labels))

print("Printing predicted quantities")
print(str(myCombinedFP1.predicted_quantity))
print(str(myCombinedFP2.predicted_quantity))
print(str(myCombinedFP3.predicted_quantity))
print(str(myCombinedFPU.predicted_quantity))

print("Creating a machine learning model from the combine FP")
myMLModel = lrn.MLModel([myCombinedFP1, myCombinedFP2,
                         myCombinedFP3, myCombinedFPU], lrn.MLAlgorithm.decision_tree)

print("Testing recognition of ChangesetU")
print(str(myMLModel.predict(myCombinedFPU)))
print("Testing recognition of Changeset2")
print(str(myMLModel.predict(myCombinedFP2)))

dswd.mark()
print("Now, undo the action you performed during the last break")
ipdb.set_trace()

dswd.mark()
time.sleep(3)
print("Cool, now redo that action")
ipdb.set_trace()


print("Marking...")
testcsU2 = dswd.mark()
print("Creating a combined fingerprint from that action")
myCombinedFPU2 = fp.changeset_to_fingerprint(testcsU2, fp.FingerprintingMethod.combined,
                                             filetree_dictionary=myFTDict,
                                             neighbor_dictionary=myNDict)
print("Testing recognition of that action (should print ChangesetU)")
print(str(myMLModel.predict(myCombinedFPU2)))

print("-------BEGIN API TESTING-------")
print("Ensure Redis Server and RQ worker are running")
import requests
import pickle
print("Saving model to /tmp/DS_MLModel")
pickle.dump(myMLModel, open("/tmp/DS_MLModel", mode='wb'))
# url = "http://127.0.0.1:8000/fingerprint/submit/"
# data = { "fingerprint" : pickle.dumps(myCombinedFPU2)}
print("Submitting myCombinedFPU2 to API. Job ID will print below")
r = net.submit_fingerprint(myCombinedFPU2)
print(str(r.status_code) + ": " + r.text)

print("All done!")

print("Destroying Client Watchdog")
del dswd
