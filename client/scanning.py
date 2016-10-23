# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
"""
DeltaSherlock client scanning module. Contains methods for analyzing the
filesystem and creating changesets.
"""
import time
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

class DeltaSherlockEventHandler(PatternMatchingEventHandler):
    """
    Default handler for filesystem events. Called on each file creation,
    modification, deletion, and move.
    """
    def __init__(self, changeset, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        super(DeltaSherlockEventHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.current_changeset = changeset

    def on_created(self, event):
        self.current_changeset.add_creation_record(event.src_path, time.time())

    def on_modified(self, event):
        self.current_changeset.add_modification_record(event.src_path, time.time())

    def on_deleted(self, event):
        self.current_changeset.add_deletion_record(event.src_path, time.time())

    def on_moved(self, event):
        # Treated as a deletion of the source and a creation of the destination
        self.current_changeset.add_deletion_record(event.src_path, time.time())
        self.current_changeset.add_deletion_record(event.dest_path, time.time())


    def replace_changeset(self, new_changeset):
        """
        Swap out the current changeset being recorded to with a new changeset.
        Return the old, closed changeset
        """
        if not new_changeset.open:
            raise ValueError("Cannot give a closed changeset to event handler")

        old_changeset = self.current_changeset
        self.current_changeset = new_changeset
        old_changeset.close(time.time())
        return old_changeset

class ChangesetRecord(object):
    """
    Container for an filesystem change record
    """
    def __init__(self, filename, mtime):
        self.filename = filename
        self.mtime = mtime

    def sentence(self):
        """
        Return the sentence this record represents in the form of a list of
        words
        """
        return list(filter(None, self.filename.split("/")))

    def __lt__(self, other):
        return self.mtime < other.mtime

class Changeset(object):
    """
    Represents all filesystem changes during a certain interval (between its
    open_time and close_time)
    """
    def __init__(self, open_time):
        # Define the interval that the changeset covers
        # (or at least the start of it)
        self.open_time = open_time
        self.open = True
        self.close_time = -1

        self.creations = []
        self.modifications = []
        self.deletions = []
        return

    def add_creation_record(self, filename, mtime):
        self.creations.append(ChangesetRecord(filename, mtime))
        return

    def add_modification_record(self, filename, mtime):
        self.modifications.append(ChangesetRecord(filename, mtime))
        return

    def add_deletion_record(self, filename, mtime):
        self.deletions.append(ChangesetRecord(filename, mtime))
        return

    def close(self, close_time):
        """
        Close changeset, indicating that no further changes should be recorded
        """
        self.close_time = close_time
        self.open = False

    def get_sentences(self):
        """
        Produces a list of sentences (which are just lists of words)
        corresponding to all changes within the set. Can only be called after
        changeset is closed
        """
        # Only usable once record is closed
        if self.open:
            raise ValueError("Cannot obtain sentences from an open changeset")

        sentences = []

        for record in self.creations:
            sentences.append(record.sentence())
        for record in self.modifications:
            sentences.append(record.sentence())
        for record in self.deletions:
            sentences.append(record.sentence())

        return sentences

    def sort(self):
        """
        Sorts all internal records by mtime
        """
        self.creations = sorted(self.creations)
        self.modifications = sorted(self.modifications)
        self.deletions = sorted(self.deletions)

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


class DeltaSherlockWatchdog(object):
    def __init__(self, path, patterns, ignore_patterns):
        # Create changeset infrastructure
        self.__changesets = []

        self.__observer = Observer()
        self.__handler = DeltaSherlockEventHandler(Changeset(time.time()), patterns=patterns, ignore_patterns=ignore_patterns, ignore_directories=True, case_sensitive=False)
        self.__observer.schedule(self.__handler, path, recursive=True)
        self.__observer.start()

    def __del__(self):
        self.__observer.stop()
        # Block until thread has stopped
        self.__observer.join()

    def mark(self):
        """
        Close the current changeset being recorded to, open a new one, and
        return the former
        """
        latest_changeset = self.__handler.replace_changeset(Changeset(time.time()))
        self.__changesets.append(latest_changeset)
        return latest_changeset

    def get_changeset(self, first_index, last_index = None):
        """
        Returns the sum of all changesets between two indexes (inclusive of
        first, exclusive of last), or just the single changeset specified
        """
        sum_changeset = self.__changesets[first_index]

        if last_index is not None:
            for changeset in self.__changesets[first_index+1:last_index]:
                sum_changeset += changeset

        return sum_changeset
