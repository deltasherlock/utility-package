import client.scanning
import common.dictionaries
import time

print("Creating DeltaSherlockWatchdog...")
dswd = client.scanning.DeltaSherlockWatchdog("/home/ubuntu/test", "*", ".")

print("Waiting 20 sec...")
time.sleep(20)

print("Marking...")
testcs = dswd.mark()

print("Printing sentences...")
print(testcs.get_sentences())

print("Creating dictionary...")
myDict = common.dictionaries.create_dictionary(testcs.get_sentences(), threads=1)

print("Trying sanity check...")
print(myDict.doesnt_match("var log syslog kitty".split()))

print("Destroying")
del dswd

print("All done!")
