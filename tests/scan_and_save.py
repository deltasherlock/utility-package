"""
DeltaSherlock Client Scanning Test

Demonstrates the creation of a changeset and fingerprint from some random
filesystem activity
"""
# pylint: disable=C0103
import time
import tempfile
from deltasherlock.common import fingerprinting as fp
from deltasherlock.common import dictionaries as dc
from deltasherlock.client.ds_watchdog import DeltaSherlockWatchdog
from deltasherlock.server import learning as lrn
from deltasherlock.common.io import random_activity, uid

# def uid(size=6, chars=string.ascii_uppercase + string.digits):
#     """Generates a nice short unique ID for random files"""
#     return ''.join(random.choice(chars) for _ in range(size))
#
# def random_activity(testdirpath):
#     files_created = []
#     for i in range(10):
#         files_created.append(tempfile.mkstemp(dir=testdirpath, suffix=str(uid())))
#     testsubdirpath = os.path.join(testdirpath, str(uid()))
#     os.mkdir(testsubdirpath)
#     time.sleep(2)
#     for i in range(15):
#         files_created.append(tempfile.mkstemp(dir=testsubdirpath, suffix=str(uid())))
#     time.sleep(2)
#
#     return files_created

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


print("Creating a histogram fingerprint")
myHistogramFP1 = fp.changeset_to_fingerprint(
    testcs1, fp.FingerprintingMethod.histogram)
myHistogramFP2 = fp.changeset_to_fingerprint(
    testcs2, fp.FingerprintingMethod.histogram)
myHistogramFP3 = fp.changeset_to_fingerprint(
    testcs3, fp.FingerprintingMethod.histogram)
myHistogramFPU = fp.changeset_to_fingerprint(
    testcsU, fp.FingerprintingMethod.histogram)

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

print("Saving all changesets & combined fingerprints generated here (Pickle, Base-64 encoded)")
from deltasherlock.common.io import save_object_as_base64
save_object_as_base64(testcs1, "myCS1.cs64")
save_object_as_base64(testcs2, "myCS2.cs64")
save_object_as_base64(testcs3, "myCS3.cs64")
save_object_as_base64(testcsU, "myCSU.cs64")
save_object_as_base64(myCombinedFP1, "myCombinedFP1.fp64")
save_object_as_base64(myCombinedFP2, "myCombinedFP2.fp64")
save_object_as_base64(myCombinedFP3, "myCombinedFP3.fp64")
save_object_as_base64(myCombinedFPU, "myCombinedFPU.fp64")
save_object_as_base64(myCombinedFPU2, "myCombinedFPU2.fp64")

print("All done! Dropping to debugger to allow for final inspection")
ipdb.set_trace()
print("Destroying Client Watchdog")
del dswd
