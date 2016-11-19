# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
# pylint: disable=W0141
"""
DeltaSherlock changeset types
"""
from os import listdir
from os.path import dirname, basename, isfile
from itertools import chain


class ChangesetRecord(object):
    """
    Container for an filesystem change record
    """
    def __init__(self, filename: str, mtime: int, neighbors: str = list()):
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
        return [basename(self.filename)] + self.neighbors

    # def add_neighbor(self, filename: str):
    #     """
    #     Add a record for a file that coexists inside the same directory as this
    #     record's file. Filename should not include path
    #     """
    #     self.neighbors.append(filename)
    #     return

    def find_neighbors(self):
        """
        Get all of the "neighbors" of this file (eg. files that also exist in
        the same directory) and save the results in the list
        """
        try:
            excluded_entries = [basename(self.filename), ".", ".."]
            files = [f for f in listdir(dirname(self.filename)) if isfile(f)]
            self.neighbors = list(set(files) - set(excluded_entries))
        except:
            raise IOError("Neighors could not be obtained")
        return

    def basename(self) -> str:
        """
        Returns the basename of the record's filename
        """
        return basename(self.filename)

    def __lt__(self, other):
        """
        Allows comparison by mtime
        """
        return self.mtime < other.mtime

    def __gt__(self, other):
        """
        Allows comparison by mtime
        """
        return self.mtime > other.mtime


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
        if not self.open:
            raise ValueError("Cannot modify closed Changeset")

        self.creations.append(ChangesetRecord(filename, mtime))
        return

    def add_modification_record(self, filename: str, mtime: int):
        if not self.open:
            raise ValueError("Cannot modify closed Changeset")

        self.modifications.append(ChangesetRecord(filename, mtime))
        return

    def add_deletion_record(self, filename: str, mtime: int):
        if not self.open:
            raise ValueError("Cannot modify closed Changeset")

        self.deletions.append(ChangesetRecord(filename, mtime))
        return

    def close(self, close_time: int):
        """
        Close changeset, indicating that no further changes should be recorded.
        Then balance the records lists so that temporary files that were created
        and deleted during the interval are not considered "created"
        """
        # First, balance and sort our records
        self.__balance()
        self.__sort()

        #Now that everything is balanced, find the neighbors of each changeset record
        for record in chain(self.creations, self.modifications, self.deletions):
            try:
                record.find_neighbors()
            except IOError:
                # File or containing directory no longer exists
                #TODO Log this? Probably can't do much else about this
                pass

        #And finally, set the close markers
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
        if self.open:
            raise ValueError("Cannot predict quatity on an open changeset")

        # First, figure out the bounds of our histogram
        self.__sort()
        minimum = float(self.creations[0].mtime)
        maximum = float(self.creations[-1].mtime)
        interval = int(maximum - minimum) + 1

        # Then, try to create the empty histogram
        try:
            fileHistogram = [[] for i in range(0, interval, 1)]
        except OverflowError:
            print("Overly big histogram. Skipping...")
            return 1

        # Organize creations into the histogram
        for entry in self.creations:
            fileHistogram[int(entry.mtime - minimum)].append(entry)

        # Prep for analysis
        empty_count = 0
        clusters = 0
        flag = False
        lastFlag = False
        cluster_list = []
        timeHistogram = []

        # Analyze
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

        # All done!
        return len(cluster_list)

    def __sort(self):
        """
        Sorts all internal records by mtime
        """
        self.creations = sorted(self.creations)
        self.modifications = sorted(self.modifications)
        self.deletions = sorted(self.deletions)
        return

    def __balance(self):
        """
        Create a proper "delta" by pruning all records lists of entries that
        were both created and deleted within the same changeset. Ususally only
        called by close()
        """
        for deletion_record in self.deletions:
            #Make sure we're not working with a None (you'll see why in a sec)
            if deletion_record is not None:
                #If a created file was subsequently deleted within the same interval
                #either the creation record or the deletion record has to go. The
                #older record gets the axe
                for creation_record in self.creations:
                    if creation_record is not None:
                        if deletion_record.filename == creation_record.filename:
                            try:
                                if deletion_record > creation_record:
                                    #Remember, never change the size of a list while you
                                    #iterate over it! Instead, we just replace it with None
                                    #and take it out later
                                    self.creations[self.creations.index(creation_record)] = None
                                else:
                                    self.deletions[self.deletions.index(deletion_record)] = None
                            except ValueError:
                                #This usually just means that we already
                                #deleted the record for some other reason.
                                #No biggie
                                pass

            # Check again, just to make sure we didn't delete the current record
            if deletion_record is not None:
                #Same goes for modification records
                for modification_record in self.modifications:
                    if modification_record is not None:
                        if deletion_record.filename == modification_record.filename:
                            try:
                                if deletion_record > modification_record:
                                    self.modifications[self.modifications.index(modification_record)] = None
                                else:
                                    self.deletions[self.deletions.index(deletion_record)] = None
                            except ValueError:
                                pass

        #Finally, clean the list of Nones
        self.creations = list(filter(None, self.creations))
        self.deletions = list(filter(None, self.deletions))
        self.modifications = list(filter(None, self.modifications))

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
