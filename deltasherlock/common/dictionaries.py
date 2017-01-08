"""
DeltaSherlock common dictionary-related data models and helpers.
"""
import os
import gensim


class SentencesFromDirectory(object):
    """Create an iterable object from a directory full of sentence files"""

    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()


class SentencesFromFile(object):
    """Create an iterable object from a single sentence file"""

    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        for line in open(os.path.abspath(self.filename)):
            yield line.split()


def create_dictionary(sentences, threads=4):
    """
    Create a w2v dictionary from a sentence iterable

    :param sentences: an iterable object (eg an array) containing the sentences
    :param threads: how many workers to make w2v use (default: 4)
    :returns: the dictionary (may take a while)
    """
    model = gensim.models.Word2Vec(
        sentences, size=200, workers=threads, min_count=1)
    return model
