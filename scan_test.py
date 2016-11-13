import client.scanning
import common.dictionaries
import time
import os
import tempfile
import string
import random

def uid(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

testdirpath = tempfile.mkdtemp(suffix=str(uid()))
print("Created test directory " + testdirpath)

print("Creating DeltaSherlockWatchdog...")
dswd = client.scanning.DeltaSherlockWatchdog(testdirpath, "*", ".")

print("Waiting 2 sec...")
time.sleep(2)

files_created = []
print("Creating some file activity...")
for i in range(10):
    files_created.append(tempfile.mkstemp(dir=testdirpath, suffix=str(uid())))
testsubdirpath=os.path.join(testdirpath, str(uid()))
os.mkdir(testsubdirpath)
time.sleep(2)
for i in range(5):
    files_created.append(tempfile.mkstemp(dir=testsubdirpath, suffix=str(uid())))

print("Marking...")
testcs = dswd.mark()

print("Printing neighbor sentences...")
print(testcs.get_neighbor_sentences())

print("Printing filetree sentences...")
print(testcs.get_filetree_sentences())

print("Creating neighbor dictionary...")
myNDict = common.dictionaries.create_dictionary(testcs.get_neighbor_sentences(), threads=1)

print("Creating filetree dictionary...")
myFTDict = common.dictionaries.create_dictionary(testcs.get_filetree_sentences(), threads=1)

print("Skipping neighbor sanity check...")
#print(myNDict.doesnt_match("tmp tmpi".split()))

print("Trying filetree sanity check...")
print(myFTDict.doesnt_match("tmp tmpi".split()))

print("Destroying")
del dswd

print("All done!")
