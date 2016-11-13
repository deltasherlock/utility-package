# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock changeset types
"""
from os import listdir
from os.path import dirname,basename,isfile

class ChangesetRecord(object):
    """
    Container for an filesystem change record
    """
    def __init__(self, filename: str, mtime: int, neighbors: str = None):
        self.filename = filename
        self.mtime = mtime
        self.neighbors = neighbors
        return

    def filetree_sentence(self) -> list:
        """
        Return the sentence this record represents in the form of a list of
        words (filetree)
        """
        return list(filter(None, self.filename.split("/")))

    def neighbor_sentence(self) -> list:
        """
        Return the sentence this record represents in the form of a list of
        words (neighbor)
        """
        return [basename(self.filename)]+self.neighbors

    def add_neighbor(self, filename: str):
        """
        Add a record for a file that coexists inside the same directory as this
        record's file. Filename should not include path
        """
        self.neighbors.append(filename)
        return

    def basename(self) -> str:
        """
        Returns the basename of the record's filename
        """
        return basename(self.filename)

    def __lt__(self, other):
        return self.mtime < other.mtime

class Changeset(object):
    """
    Represents all filesystem changes during a certain interval (between its
    open_time and close_time)
    """
    def __init__(self, open_time: int):
        # Define the interval that the changeset covers
        # (or at least the start of it)
        self.open_time = open_time
        self.open = True
        self.close_time = -1

        self.creations = []
        self.modifications = []
        self.deletions = []

        self.labels = []
        return

    def add_creation_record(self, filename: str, mtime: int):
        self.creations.append(ChangesetRecord(filename, mtime, self.__get_neighbors(filename)))
        return

    def add_modification_record(self, filename: str, mtime: int):
        self.modifications.append(ChangesetRecord(filename, mtime, self.__get_neighbors(filename)))
        return

    def add_deletion_record(self, filename: str, mtime: int):
        self.deletions.append(ChangesetRecord(filename, mtime, self.__get_neighbors(filename)))
        return

    def close(self, close_time: int):
        """
        Close changeset, indicating that no further changes should be recorded
        """
        self.close_time = close_time
        self.open = False
        return

    def get_filetree_sentences(self) -> list:
        """
        Produces a list of filetree sentences (which are just lists of words)
        corresponding to all changes within the set. Can only be called after
        changeset is closed
        """
        # Only usable once record is closed
        if self.open:
            raise ValueError("Cannot obtain sentences from an open changeset")

        sentences = []

        for record in self.creations:
            sentences.append(record.filetree_sentence())
        for record in self.modifications:
            sentences.append(record.filetree_sentence())
        for record in self.deletions:
            sentences.append(record.filetree_sentence())

        return sentences

    def get_neighbor_sentences(self) -> list:
        """
        Produces a list of neighbor sentences (which are just lists of words)
        corresponding to all changes within the set. Can only be called after
        changeset is closed
        """
        # Only usable once record is closed
        if self.open:
            raise ValueError("Cannot obtain sentences from an open changeset")

        sentences = []

        for record in self.creations:
            sentences.append(record.neighbor_sentence())
        for record in self.modifications:
            sentences.append(record.neighbor_sentence())
        for record in self.deletions:
            sentences.append(record.neighbor_sentence())

        return sentences

    def get_basenames(self) -> list:
        """
        Returns a list of basenames of all files changed within the interval,
        duplicates removed. Can only be called after changeset is closed
        """
        # Only usable once record is closed
        if self.open:
            raise ValueError("Cannot obtain basenames from an open changeset")

        basenames = []

        for record in self.creations:
            basenames.append(record.basename())
        for record in self.modifications:
            basenames.append(record.basename())
        for record in self.deletions:
            basenames.append(record.basename())

        return list(set(basenames))

    def add_label(self, label: str):
        """
        Labels will most likely be used to store tags for which apps
        """
        self.labels.append(label)
        return

    def predict_quantity(self) -> int:
        """
        Uses histogram analysis to make an educated guess as to how many
        installations occured within this changeset. Only looks at file creations

        :returns: the predicted quantity of apps
        """
        #First, figure out the bounds of our histogram
        self.sort()
        minimum = float(self.creations[0].mtime)
        maximum = float(self.creations[-1].mtime)
        interval = int(maximum - minimum) + 1

        #Then, try to create the empty histogram
        try:
            fileHistogram = [[] for i in range(0, interval, 1)]
        except OverflowError:
            print("Overly big histogram. Skipping...")
            return 1

        #Organize creations into the histogram
        for entry in self.creations:
            fileHistogram[int(entry.mtime - minimum)].append(entry)

        #Prep for analysis
        empty_count = 0
        clusters = 0
        flag = False
        lastFlag = False
        cluster_list = []
        timeHistogram = []

        #Analyze
        for index, histBin in enumerate(fileHistogram):
            numChanges = len(histBin)
            if numChanges > 2:
                flag = True
                empty_count = 0

            else:
                empty_count += 1
                if empty_count == 3:
                    flag = False

            if lastFlag is False and flag is True:
                clusters += 1
                cluster_begin = index
            if lastFlag is True and flag is False:
                cluster_end = index
                cluster_list.append((cluster_begin, cluster_end))

            lastFlag = flag
            timeHistogram.append(numChanges)

        #All done!
        return len(cluster_list)

    def sort(self):
        """
        Sorts all internal records by mtime
        """
        self.creations = sorted(self.creations)
        self.modifications = sorted(self.modifications)
        self.deletions = sorted(self.deletions)
        return

    def __add__(self, other):
        """
        Enables "adding" (read: combining) of two closed changesets
        """
        if self.open or other.open:
            raise ArithmeticError("Cannot add open changesets")

        lowest_open_time = self.open_time if self.open_time < other.open_time else other.open_time
        highest_close_time = self.close_time if self.close_time > other.close_time else other.close_time

        sum_changeset = Changeset(lowest_open_time)
        sum_changeset.creations = sorted(self.creations + other.creations)
        sum_changeset.modifications = sorted(self.modifications + other.modifications)
        sum_changeset.deletions = sorted(self.deletions + other.deletions)
        sum_changeset.close(highest_close_time)

        return sum_changeset

    def __get_neighbors(self, filepath: str) -> list:
        """
        Get all of the "neighbors" of a given file (eg. files that also exist in
        the same directory)
        """
        excluded_entries = [basename(filepath), ".", ".."]
        files = [f for f in listdir(dirname(filepath)) if isfile(f)]
        return list(set(files) - set(excluded_entries))
