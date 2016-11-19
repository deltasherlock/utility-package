"""
DeltaSherlock Client Scanning Test

Demonstrates the creation of a changeset and fingerprint from some random
filesystem activity
"""
# pylint: disable=C0103
import time
import os
import tempfile
import string
import random
from deltasherlock.common import fingerprinting as fp
from deltasherlock.common import dictionaries as dc
from deltasherlock.client.ds_watchdog import DeltaSherlockWatchdog

def uid(size=6, chars=string.ascii_uppercase + string.digits):
    """Generates a nice short unique ID for random files"""
    return ''.join(random.choice(chars) for _ in range(size))

testdirpath = tempfile.mkdtemp(suffix=str(uid()))
print("Created test directory " + testdirpath)

watch_paths = [testdirpath, "/var/", "/bin/", "/usr/", "/etc/"]

print("Creating DeltaSherlockWatchdog...")
dswd = DeltaSherlockWatchdog(watch_paths, "*", ".")

print("Breaking... Feel free to install something now")
import ipdb; ipdb.set_trace()
print("Waiting 2 sec...")
time.sleep(2)

files_created = []
print("Creating some file activity...")
for i in range(10):
    files_created.append(tempfile.mkstemp(dir=testdirpath, suffix=str(uid())))
testsubdirpath = os.path.join(testdirpath, str(uid()))
os.mkdir(testsubdirpath)
time.sleep(2)
for i in range(15):
    files_created.append(tempfile.mkstemp(dir=testsubdirpath, suffix=str(uid())))

print("Marking...")
testcs = dswd.mark()

print("Printing neighbor sentences...")
print(testcs.get_neighbor_sentences())

print("Printing filetree sentences...")
print(testcs.get_filetree_sentences())

print("Creating neighbor dictionary...")
myNDict = dc.create_dictionary(testcs.get_neighbor_sentences(), threads=1)

print("Creating filetree dictionary...")
myFTDict = dc.create_dictionary(testcs.get_filetree_sentences(), threads=1)

#print("Trying neighbor sanity check...")
#print(myNDict.doesnt_match("tmp tmpi".split()))

#print("Trying filetree sanity check...")
#print(myFTDict.doesnt_match("tmp tmpi".split()))

print("Destroying Client Watchdog")
del dswd

print("Creating a histogram fingerprint")
myHistogramFP = fp.changeset_to_fingerprint(testcs, fp.FingerprintingMethod.histogram)

print("Printing that...")
print(myHistogramFP)
print(str(len(myHistogramFP)))

print("Creating a combined fingerprint")
myCombinedFP = fp.changeset_to_fingerprint(testcs, fp.FingerprintingMethod.combined,
                                           filetree_dictionary=myFTDict,
                                           neighbor_dictionary=myNDict)

print("Printing that...")
print(myCombinedFP)

print("All done!")
